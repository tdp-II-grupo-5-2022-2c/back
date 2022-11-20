from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from app.db.impl.sticker_manager import StickerManager, GetStickerManager
from typing import List, Dict, Union
import csv
from app.firebase import uploadFile
import math

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
):
    try:
        if top5 is None:
            top5 = False

        result = await sticker_manager.get_sticker_metrics_freq(top5=top5)
        if generate_binary is not None and generate_binary is True:
            result = await calculatePercentage(result)
            generateCSV(result)
            uploadFile('stickers_freq.csv')

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


async def calculatePercentage(stickers: List[Dict]) -> List[Dict]:
    sticker_manager = await GetStickerManager()
    packageCounter = await sticker_manager.get_package_counter() # ToDo reiniciar package-counter para que tenga sentido la metrica

    for s in stickers:
        s['percentage'] = round(s['counter'] / packageCounter.counter * 100, 2)

    return stickers
