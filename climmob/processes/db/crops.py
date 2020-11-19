from ...models import mapFromSchema, Crops, CropAlias

__all__ = ["getListOfCrops", "existsCropByCode", "getListOfCropsByLanguaje"]


def getListOfCropsByLanguaje(request, lang_code):
    result = (
        request.dbsession.query(CropAlias)
        .filter(CropAlias.lang_code == lang_code)
        .all()
    )

    if result:
        return mapFromSchema(result)
    else:
        return False


def getListOfCrops(request):

    result = (
        request.dbsession.query(Crops, CropAlias)
        .filter(Crops.crop_cod == CropAlias.crop_cod)
        .filter(CropAlias.lang_code == request.locale_name)
        .order_by(CropAlias.alias_name)
        .all()
    )

    if result:
        return mapFromSchema(result)
    else:
        return False


def existsCropByCode(request, crop_code, alias_cod, lang_code):
    results = (
        request.dbsession.query(CropAlias)
        .filter(CropAlias.crop_cod == crop_code)
        .filter(CropAlias.alias_cod == alias_cod)
        .filter(CropAlias.lang_code == lang_code)
        .first()
    )

    if results:
        return True
    else:
        return False
