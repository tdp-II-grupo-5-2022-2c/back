from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.db.impl.report_manager import ReportManager, GetReportManager
from app.db.impl.sticker_manager import StickerManager, GetStickerManager
from typing import List, Dict, Union
import csv

from app.db.impl.user_manager import GetUserManager, UserManager
from app.db.model.report import AlbumCompletionReport
from app.firebase import FirebaseManager, GetFirebaseManager

router = APIRouter(tags=["reports"])


@router.get(
    "/reports/stickers-metrics-freq",
    response_description="Get top 5 stickers metrics",
    status_code=status.HTTP_200_OK,
)
async def get_sticker_metrics(
        top5: Union[bool, None] = None,
        generate_binary: Union[bool, None] = None,
        sticker_manager: StickerManager = Depends(GetStickerManager),
        firebase_manager: FirebaseManager = Depends(GetFirebaseManager),
):
    try:
        if top5 is None:
            top5 = False

        result = await sticker_manager.get_sticker_metrics_freq(top5=top5)
        if generate_binary is not None and generate_binary is True:
            result = await calculatePercentage(sticker_manager, result)
            generateCSV(result)
            firebase_manager.uploadFile('stickers_freq.csv')

        return result
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Unexpected error getting stickers freq report. Exception: {e}"
        )


def generateCSV(stickers: List[Dict]):
    with open('stickers_freq.csv', 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, ['name', 'country', 'counter', 'percentage'])
        dict_writer.writeheader()
        dict_writer.writerows(stickers)


async def calculatePercentage(sticker_manager: StickerManager, stickers: List[Dict]) -> List[Dict]:
    # ToDo reiniciar package-counter para que tenga sentido la metrica
    packageCounter = await sticker_manager.get_package_counter()

    for s in stickers:
        s['percentage'] = round(s['counter'] / packageCounter.counter * 100, 2)

    return stickers


@router.post(
    "/reports/album-completion",
    response_description="Get users album completion percentage",
    response_model=str,
    status_code=status.HTTP_200_OK,
)
async def get_album_completion_report(
        manager: ReportManager = Depends(GetReportManager),
        user_manager: UserManager = Depends(GetUserManager),
):
    try:
        users = await user_manager.get_all()

        report = AlbumCompletionReport()
        for user in users:
            album_completion = user.album_completion_pct

            if album_completion < 20:
                report.p20 += 1
            elif album_completion < 40:
                report.p40 += 1
            elif album_completion < 60:
                report.p60 += 1
            elif album_completion < 80:
                report.p80 += 1
            else:
                report.p100 += 1

        await manager.save_album_completion_report(report)
        return "Report generated"
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not generate album completion report. Exception: {e}"
        )


@router.get(
    "/reports/album-completion",
    response_description="Get users album completion percentage",
    response_model=AlbumCompletionReport,
    status_code=status.HTTP_200_OK,
)
async def get_album_completion_report(
        date: str,
        manager: ReportManager = Depends(GetReportManager),
):
    try:
        response = await manager.get_album_completion_report(date)
        return response
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Could not generate album completion report. Exception: {e}"
        )
