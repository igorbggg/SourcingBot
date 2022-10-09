from db_tools.mongo_tools.crud import get_ap_data_from_cloud


def test_get_ap_data_from_cloud():
    text_uid = '6341344e0dc02'

    result = get_ap_data_from_cloud(text_uid)

    print(result)

    assert result
