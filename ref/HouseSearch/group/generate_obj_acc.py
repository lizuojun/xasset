import math

from Extract.extract_cache import get_house_data, get_house_sample, get_furniture_data, rot_to_ang
from House.house_service import get_scene_json_daily, get_design_json_daily
import json

all_design_data = [
    {
        "id": "design_1",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "9月26日",
        "name": "72方现代简约客餐厅样板间",
        "area": "72",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01Q8oImV1MHpAfBJv31_!!6000000001410-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=6be61SrD61on3H5bQ3u5U1",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.44627f97o9ffSe&assetId=475583d7-adcb-48c5-aa12-81d6682d23f8"
    },
    {
        "id": "design_2",
        "style": "现代简约",
        "space": "主卧室",
        "time": "9月26日",
        "name": "72方现代简约卧室样板间",
        "area": "72",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01vnk6MC1OoScnnHpyc_!!6000000001752-0-tps-4000-3000.jpg",
        "3d": "https://pano.shejijia.com/?sid=6be61SrD61on3H5bQ3u5U1",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.44627f97o9ffSe&assetId=475583d7-adcb-48c5-aa12-81d6682d23f8"
    },
    {
        "id": "design_3",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "9月24日",
        "name": "70方现代简约客餐厅样板间",
        "area": "70",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01099HWb1WpqkcYnZt3_!!6000000002838-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com/?sid=vuSRqrRM6G7ASaMFDMuwuZ&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=665cf321-2494-4c68-833a-42fcbf3e6df6"
    },
    {
        "id": "design_4",
        "style": "现代简约",
        "space": "主卧室",
        "time": "9月24日",
        "name": "70方现代简约卧室样板间",
        "area": "70",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01o8PcIb1O1udt05x4W_!!6000000001646-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=vuSRqrRM6G7ASaMFDMuwuZ&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=665cf321-2494-4c68-833a-42fcbf3e6df6"
    },
    {
        "id": "design_5",
        "style": "北欧",
        "space": "客餐厅",
        "time": "9月23日",
        "name": "100方北欧客餐厅样板间",
        "area": "100",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01FKIv4d1LgGh3MZI0w_!!6000000001328-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com/?sid=pMjesHeXKDvGNBzZFbckBd",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=51ae2ea7-8e54-48f4-92a9-51fa6fe687f5"
    },
    {
        "id": "design_6",
        "style": "北欧",
        "space": "主卧室",
        "time": "9月23日",
        "name": "100方北欧卧室样板间",
        "area": "100",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01s9wPEW1V2YVY8lEWW_!!6000000002595-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=pMjesHeXKDvGNBzZFbckBd",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=51ae2ea7-8e54-48f4-92a9-51fa6fe687f5"
    },
    {
        "id": "design_7",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月9日",
        "name": "127方北欧客餐厅样板间",
        "area": "127",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01j6ANbA1r5glLJy9ph_!!6000000005580-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com/?sid=wLb37JpeoH2Wy3aa1VSLct&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.23b67f976P3nz8&assetId=703f375e-07f1-421e-a174-52baad2aa1b7"
    },
    {
        "id": "design_8",
        "style": "北欧",
        "space": "主卧室",
        "time": "10月9日",
        "name": "127方北欧卧室样板间",
        "area": "127",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01idXQ811VXhRGMApwo_!!6000000002663-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com/?sid=wLb37JpeoH2Wy3aa1VSLct&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.23b67f976P3nz8&assetId=703f375e-07f1-421e-a174-52baad2aa1b7"
    },
    {
        "id": "design_9",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月15日",
        "name": "90方现代简约客餐厅样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN012d3WrM1sL5hJuPEEp_!!6000000005749-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=cPLpLp8JZJsCR49ohbgxZK&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.3d297f97rg1fTG&assetId=7c7dcb6f-e05e-47a8-8834-a45e67276f78"
    },
    {
        "id": "design_10",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月15日",
        "name": "90方现代简约卧室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN016PdszX22FjDg34sku_!!6000000007091-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=cPLpLp8JZJsCR49ohbgxZK&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.3d297f97rg1fTG&assetId=7c7dcb6f-e05e-47a8-8834-a45e67276f78"
    },
    {
        "id": "design_11",
        "style": "北欧",
        "space": "主卧室",
        "time": "10月15日",
        "name": "120方北欧卧室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01qeied322qMu69rGPv_!!6000000007171-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=97XRMLtTgpaa4f1dAzV2dY",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=e1b8adb9-bab3-4d07-8f9b-b6e40b614be9"
    },
    {
        "id": "design_12",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月15日",
        "name": "120方北欧客餐厅样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01zwpW8F1Ztv7SPRuDZ_!!6000000003253-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com/?sid=97XRMLtTgpaa4f1dAzV2dY",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=e1b8adb9-bab3-4d07-8f9b-b6e40b614be9"
    },
    {
        "id": "design_13",
        "style": "北欧",
        "space": "卧室",
        "time": "10月15日",
        "name": "120方北欧卧室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01UzhLkS25ljkIwnbHG_!!6000000007567-0-tps-1756-901.jpg",
        "3d": "https://pano.shejijia.com/?sid=kSkFuiebhfDy7eXFo6VtGk",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=cd1863c7-301e-4dd7-a013-1c3ba092dd8e"
    },
    {
        "id": "design_14",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月15日",
        "name": "120方北欧客餐厅样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01zFe8ES22vrelq1Uq3_!!6000000007183-0-tps-1766-896.jpg",
        "3d": "https://pano.shejijia.com/?sid=kSkFuiebhfDy7eXFo6VtGk",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=cd1863c7-301e-4dd7-a013-1c3ba092dd8e"
    },
    {
        "id": "design_15",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月15日",
        "name": "90方现代卧室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01bm4REI1JR2HzOdslo_!!6000000001024-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=enE8nTrFZsrTzACma7mUZe",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=79447879-6a46-45b3-9b30-ccedd519cb00"
    },
    {
        "id": "design_16",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月15日",
        "name": "90方现代客餐厅样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01enXJpA1O1udoccfxn_!!6000000001646-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=enE8nTrFZsrTzACma7mUZe",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=79447879-6a46-45b3-9b30-ccedd519cb00"
    },
    {
        "id": "design_17",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月18日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01GUc07G1c8EjJpsOiY_!!6000000003555-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=kYLzwBV3V6Cf1H5ZaJSwXs",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.17977f97yQ2994&assetId=63316817-486a-4d39-ba10-995801a3b7a5"
    },
    {
        "id": "design_18",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月15日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01oNHrIO1fSnM8o1Ipk_!!6000000004006-0-tps-1744-901.jpg",
        "3d": "https://pano.shejijia.com/?sid=fWn6iCNwvhXgievUJUYcTU",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=f9c1dd91-bb47-418c-affd-8d7fc81d2dd3"
    },
    {
        "id": "design_19",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月16日",
        "name": "120方北客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01TOBhYV1jI2WDZHNuT_!!6000000004524-0-tps-1787-901.jpg",
        "3d": "https://pano.shejijia.com?sid=5dAyumq5a4veac8bxPQ9z3&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=9c38feda-3d12-42fb-8a99-27b1bf05a5e0"
    },
    {
        "id": "design_20",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月17日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01ah5SBB1aWqmVM9wwr_!!6000000003338-0-tps-1789-898.jpg",
        "3d": "https://pano.shejijia.com?sid=u1YzGjE2nBeupiSuMdUC9V&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=a528eeb1-394b-4da2-aac6-afa40a08b03f"
    },
    {
        "id": "design_21",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月18日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01wjqbI61HyoGKzxXGz_!!6000000000827-0-tps-1790-899.jpg",
        "3d": "https://pano.shejijia.com?sid=j7TufSzqNa6BEJJV3HrAH5&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=c05ab99c-051e-4276-a0b4-d756ce218f5a"
    },
    {
        "id": "design_22",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月19日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01NKGZgK1mn8FoVwOf1_!!6000000004998-0-tps-1782-900.jpg",
        "3d": "https://pano.shejijia.com?sid=nusEmwK1SkbKVEuVmh19vA&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=8170b694-0f17-48ad-87e4-6304a82302e7"
    },
    {
        "id": "design_23",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月20日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01ZE6iMX1ImH2QPUei4_!!6000000000935-0-tps-1802-906.jpg",
        "3d": "https://pano.shejijia.com?sid=9nqtvyo9m5EdiNV1VhWVQY&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=83b865ca-8d5b-4f01-a872-637cf12f8be8"
    },
    {
        "id": "design_24",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月16日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01HpSsFK1lNebcZc46m_!!6000000004807-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=cnbVXYA2Jg8B4mcZZYVViC&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=489c410c-f01c-431a-b4f3-30368d066fea"
    },
    {
        "id": "design_25",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月17日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01JfHLtq1PE6nyG4op7_!!6000000001808-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=fZpfMy9AemNFiqJXhCRewt&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=6393844e-acce-4184-8f05-b6725dd7615f"
    },
    {
        "id": "design_26",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月19日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01xGg9yD1ogq2bjo81w_!!6000000005255-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=rZekeEf5HKohoSfNZn9kc7&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=cd9d0f7e-7e27-4904-a073-5df17b0f2bc0"
    },
    {
        "id": "design_27",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月20日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01n2iHGc1VfUAs4Q0ai_!!6000000002680-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=4JvQGQWE2k93XFPa1Kpmio&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=bc3fad4f-c7ea-4041-8c11-a2fb1ad4d4bd"
    },
    {
        "id": "design_28",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月15日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01GhshYG1nFWoBMsDQx_!!6000000005060-0-tps-1707-909.jpg",
        "3d": "https://pano.shejijia.com?sid=oxXQ1bbyX43j9otAKrL4am&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=f5cf9bf1-6d38-440b-8fc2-315ba26af331"
    },
    {
        "id": "design_29",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月16日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN011jMrl31NsIK9bg60c_!!6000000001625-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=iCDzcdSaKLQBvGh2aqGVbH&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=5bf2ca47-70cd-4acd-aa8c-1b40486cc67c"
    },
    {
        "id": "design_30",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月17日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01ti1b3V21yKAWwb9G4_!!6000000007053-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=mF1kx2cJQdPnuK5DoTZYje&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=296a0e9a-4d66-44bb-a5b8-3e4ea68307fb"
    },
    {
        "id": "design_31",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月18日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01HIBiXA1FWIN85BIxd_!!6000000000494-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=aaCmH5h5GKyEc4L9xuaLeS&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=2708c14e-b996-4bc5-9f37-5aec665e628f"
    },
    {
        "id": "design_32",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月19日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN010t7m4m1lf3ej3anZs_!!6000000004845-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=oZ13ieiiEN4w2iztDHwkB1&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=b8899f87-2ffb-4981-a3e8-0d5ff8848c1f"
    },
    {
        "id": "design_33",
        "style": "北欧",
        "space": "客餐厅",
        "time": "10月20日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN013PQ8bw1ZOJmrvMWrP_!!6000000003184-0-tps-1800-922.jpg",
        "3d": "https://pano.shejijia.com/?sid=kBZdC6idrcya1Pc1PW2gnE",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=f5c7153a-6457-45c9-ae3e-9428acf6c0f6"
    },
    {
        "id": "design_34",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月22日",
        "name": "120方现代简约客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01ytYXQg1zMeMBZQSGN_!!6000000006700-0-tps-1781-896.jpg",
        "3d": "https://pano.shejijia.com?sid=ojXMhdAcQZazsD8mVwSAzB&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=24f05ffb-0898-4408-98bc-c2dbb8a757ef"
    },
    {
        "id": "design_35",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月22日",
        "name": "90方现代简约客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01IWJG871b1XJvvKnDr_!!6000000003405-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=kQbyLRuUoo6KDvqSn5wzNT&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=7641c960-994d-4a9e-89ca-0c2528c41ae9"
    },
    {
        "id": "design_36",
        "style": "现代简约",
        "space": "卧室",
        "time": "10月25日",
        "name": "120方北欧卧室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01p1bBbT29O9onEuKB9_!!6000000008057-0-tps-1773-890.jpg",
        "3d": "https://pano.shejijia.com/?sid=6zBURyfpzTSmxvkk7VWtGq",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=839d2b3d-06f6-4ab7-b3e9-e5ebcc035a7f"
    },
    {
        "id": "design_37",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月25日",
        "name": "120方北欧客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN011D8GfG28QcKZClepL_!!6000000007927-0-tps-1786-898.jpg",
        "3d": "https://pano.shejijia.com/?sid=6zBURyfpzTSmxvkk7VWtGq",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=839d2b3d-06f6-4ab7-b3e9-e5ebcc035a7f"
    },
    {
        "id": "design_38",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月22日",
        "name": "90方北欧客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01rmQZlR1QIWETyXeIK_!!6000000001953-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com/?sid=uA7UL49Dk8JpgiK4abAvBc",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.4dfc7f97X8SniM&webClient=win&clientVersion=4.0.5&channelCode=2020062911272&assetId=f3c39b41-decc-47d0-a6a5-aa279e2ac8e4"
    },
    {
        "id": "design_39",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月25日",
        "name": "120方北欧卧室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN01X6DumC1vV7DQimQsD_!!6000000006177-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=wQC8tdewrHNoaLwFrss9jb&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=a7c14501-b743-4397-b850-017360bb0002"
    },
    {
        "id": "design_40",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月25日",
        "name": "120方现代简约客餐厅室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01HXc6yn1RweYPzLRQN_!!6000000002176-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=wQC8tdewrHNoaLwFrss9jb&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=a7c14501-b743-4397-b850-017360bb0002"
    },
    {
        "id": "design_41",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月25日",
        "name": "90方现代简约客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01FBFMMf1Wo1AS7NRnQ_!!6000000002834-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=iR3nAo3KBmmysF43Wjujad&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=4312dd6a-ac45-4297-b334-b042922c38ad"
    },
    {
        "id": "design_42",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月25日",
        "name": "90方现代简约客餐厅室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01UGyKGf1NeYRWh17gr_!!6000000001595-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=vrcXHGBsYa1FZWeU6q3f1g&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13184207.0.0.111d7f44rzGgue&assetId=cffb9d94-6367-4b55-a312-b14648540ede"
    },
    {
        "id": "design_43",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月25日",
        "name": "90方现代简约卧室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN013Mg9TX1WX4VfO1XXH_!!6000000002797-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=7r73F2dkSSSjcyh3YgCa5o&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13184207.0.0.111d7f44rzGgue&assetId=cffb9d94-6367-4b55-a312-b14648540ede"
    },
    {
        "id": "design_44",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月26日",
        "name": "90方现代简约卧室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01LRFASV1cisPji5dAg_!!6000000003635-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=c2ifBCEKeDbSihvjaZF1sz&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=7cafdcb4-9ce9-45fd-9748-3a72b67025a6"
    },
    {
        "id": "design_45",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月26日",
        "name": "90方现代简约客餐厅样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i1/O1CN01z6LcVj1XHKW6kHU3Z_!!6000000002898-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=sC5PeyDr2qt2FFExfexWJ5&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.50f47f97vQlvwS&assetId=8d6cd145-b2fa-4709-9e62-7165e6882fee"
    },
    {
        "id": "design_46",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月26日",
        "name": "90方现代简约卧室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01pTKk651N4pY3wN2Fh_!!6000000001517-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=xAJS6Wy9f1AebdC9ZrnC3j&locale=zh_CN",
        "design": "https://3d.shejijia.com/?spm=a214ky.13373718.0.0.50f47f97vQlvwS&assetId=8d6cd145-b2fa-4709-9e62-7165e6882fee"
    },
    {
        "id": "design_47",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月27日",
        "name": "90方现代简约客餐厅样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01lCDjUM1zBeqh4zlvH_!!6000000006676-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=agbQPZCn6MLWd9h5Mvir5M&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=ea48de3a-42b2-40f1-8fef-f4474843bac0"
    },
    {
        "id": "design_48",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月27日",
        "name": "120方现代简约卧室样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01K9OaTt20fG43UzxM7_!!6000000006876-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=uEPHMLv8DysjhGC6UmbHnt&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=96f1c068-d7b8-4615-b82b-2518ec31d90a"
    },
    {
        "id": "design_49",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月27日",
        "name": "120方现代简约客餐厅样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i4/O1CN01Voqvo51kXRSD5C5pB_!!6000000004693-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=uEPHMLv8DysjhGC6UmbHnt&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=96f1c068-d7b8-4615-b82b-2518ec31d90a"
    },
    {
        "id": "design_50",
        "style": "现代简约",
        "space": "客餐厅",
        "time": "10月28日",
        "name": "120方现代简约客餐厅样板间",
        "area": "120",
        "cover": "https://img.alicdn.com/imgextra/i2/O1CN01Y30CCQ1cvF6sx3C28_!!6000000003662-0-tps-1920-1080.jpg",
        "3d": "https://pano.shejijia.com?sid=uCydU4Sf6qDaS8ry7qhCdi&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=5bf2ca47-70cd-4acd-aa8c-1b40486cc67c"
    },
    {
        "id": "design_51",
        "style": "现代简约",
        "space": "主卧室",
        "time": "10月28日",
        "name": "90方现代简约卧室样板间",
        "area": "90",
        "cover": "https://img.alicdn.com/imgextra/i3/O1CN0121m9HQ1ntpfHeiHBj_!!6000000005148-0-tps-1600-1200.jpg",
        "3d": "https://pano.shejijia.com?sid=jSbdkhXQHU42ah2cHWYapY&locale=zh_CN",
        "design": "https://3d.shejijia.com/?env=shejishi&assetId=ea48de3a-42b2-40f1-8fef-f4474843bac0"
    }
]


def check_normal_p(obj, furniture_list):
    out_obj = []
    p = [obj["position"][0], obj["position"][2]]
    half_size = [obj["size"][0] * obj["scale"][0] / 200. * 1.05, obj["size"][2]*obj["scale"][2] / 200.* 1.05]
    rot = rot_to_ang(obj["rotation"])
    if abs(obj["rotation"][1]) > 0.5 and abs(obj["rotation"][1]) < 0.8:
        half_size = [half_size[1], half_size[0]]

    main_aabb = [[p[0] - half_size[0], p[1] - half_size[1]], [p[0] + half_size[0], p[1] + half_size[1]]]

    for target_obj in furniture_list:
        if target_obj["id"] == obj["id"]:
            continue

        now_p = [target_obj["position"][0], target_obj["position"][2]]
        now_half_size = [target_obj["size"][0]*target_obj["scale"][0] / 200., target_obj["size"][2]*target_obj["scale"][2] / 200.]
        if abs(target_obj["rotation"][1]) > 0.5 and abs(target_obj["rotation"][1]) < 0.8:
            now_half_size = [now_half_size[1], now_half_size[0]]
        now_aabb = [[now_p[0] - now_half_size[0], now_p[1] - now_half_size[1]],
                    [now_p[0] + now_half_size[0], now_p[1] + now_half_size[1]]]
        if main_aabb[0][0] < now_aabb[0][0] and now_aabb[1][0] < main_aabb[1][0] and main_aabb[0][1] < now_aabb[0][
            1] and now_aabb[1][1] < main_aabb[1][1]:
            target_rot = rot_to_ang(target_obj["rotation"])
            ang_delta = target_rot - rot
            if "lamp" in target_obj["type"]:
                if obj["size"][1] / 100. + 0.8 < target_obj["size"][1] / 100. + target_obj["position"][1]:
                    continue
            else:
                if obj["size"][1]/100. + 0.3 < target_obj["size"][1]/100. + target_obj["position"][1]:
                    continue

            out_obj.append(target_obj)

    return out_obj


temp = {
    "id": "",
    "related_list": [
        {
            "id": "",
            "normal_pos": "",
            "normal_rotation": "",
            "scale": ""
        }
    ]
}

out_all_obj = {}


def get_related_info(obj, target_obj):
    rot = rot_to_ang(obj["rotation"])
    target_rot = rot_to_ang(target_obj["rotation"])
    ang_delta = target_rot - rot

    normal_rotation = [0., math.sin(ang_delta/2.), 0., math.cos(ang_delta/2.)]

    normal_p = [target_obj["position"][0] - obj["position"][0], target_obj["position"][1] - obj["position"][1],
                target_obj["position"][2] - obj["position"][2]]
    normal_p[0], normal_p[2] = math.cos(rot) * normal_p[0] - math.sin(-rot) * normal_p[2], math.sin(rot) * normal_p[0] + math.cos(rot) * normal_p[2]


    return {
        "id": target_obj["id"],
        "normal_position": normal_p,
        "normal_rotation": normal_rotation,
        "scale": target_obj["scale"].copy()
    }


all_design_list = json.load(open("all_design_list.json", "r"))
#
#


for design_data in all_design_list:
    design_id, design_url, scene_url = design_data
    if design_id not in ["79447879-6a46-45b3-9b30-ccedd519cb00"]:
        continue

    _, house_data = get_house_data(design_id,
                                   design_url="",
                                   scene_url=scene_url,reload=True)
    print(design_id)
    sample_para, sample_data, sample_layout, sample_group = get_house_sample(design_id, reload=True)

    for room in sample_data["room"]:
        if room["type"] not in ["LivingDiningRoom", "LivingRoom", "MasterBedroom", "Bedroom", "SecondBedroom"]:
            continue

        furniture_list = room["furniture_info"]
        # if len(furniture_list) < 10:
        #     continue

        for obj in furniture_list:
            obj_type, _, _ = get_furniture_data(obj["id"])
            no_use = False
            for t in ["rug", "lighting", "sofa", "chair", "bed", "300", "200", "curtain", "accessory"]:
                if t in obj_type:
                    no_use = True
                    break
            if no_use:
                continue

            if obj["size"][0] > 0.3:
                main_pos = obj["position"]
                if obj["id"] == "6f61f213-5a5e-4471-a201-d35e32b6f675":
                    out_obj_list = check_normal_p(obj, furniture_list)
                else:
                    continue
                if out_obj_list:
                    related_list = []
                    for target_obj in out_obj_list:
                        related_list.append(get_related_info(obj, target_obj))
                    if len(related_list) > 0:
                        out_all_obj[obj["id"]] = related_list
1/0
with open("save_related_info_acc_new.json", "w") as f:
    f.write(json.dumps(out_all_obj))


base_info = json.load(open("save_related_info_acc_new.json", "r"))
add_info = json.load(open("save_related_info.json", "r"))

print()
for i in base_info:

    obj_type, _, _ = get_furniture_data(i)
    print(i, obj_type)

    flag = True
    for j in ["rug", "lighting", "sofa", "chair", "bed", "300", "200", "curtain", "accessory"]:
        if j in obj_type:
            flag = False
            break
    if flag:
        add_info[i] = base_info[i]

with open("new_save_related_info.json", "w") as f:
    f.write(json.dumps(add_info))
