import pytest
from ratings.models import AirConditioner, ParameterValue


@pytest.fixture
def sample_ac(db):
    return AirConditioner.objects.create(
        rank=1,
        brand="TestBrand",
        model_name="TestModel-X100",
        youtube_url="https://youtu.be/test123",
        rutube_url="https://rutube.ru/video/test123/",
        vk_url="https://vk.com/video-12345",
        total_score=200.5,
    )


@pytest.fixture
def sample_ac_with_params(sample_ac):
    params = [
        ("Шум мин.", "32", "дБ(А)", 36.0),
        ("Вибрация", "0.07", "мм", 4.3),
        ("Мин. напряжение", "100", "В", 5.0),
        ("S меди внутр. блок", "0.26", "", 26.0),
        ("S меди наруж. блок", "0.28", "", 28.0),
        ("Наличие ЭРВ", "нет", "", 0.0),
        ("Подсветка пульта", "есть", "", 10.0),
        ("Тип (инвертор/он-офф)", "инвертор", "", 30.0),
        ("Наличие WiFi", "Опция", "", 5.0),
        ("Регулировка оборотов наруж. бл.", "Есть", "", 10.0),
        ("Кол-во скоростей внутр. бл.", "5", "", 1.0),
        ("Макс. длина фреонопровода", "20", "м", 10.0),
    ]
    for name, value, unit, score in params:
        ParameterValue.objects.create(
            air_conditioner=sample_ac,
            parameter_name=name,
            raw_value=value,
            unit=unit,
            score=score,
        )
    return sample_ac


@pytest.fixture
def second_ac(db):
    return AirConditioner.objects.create(
        rank=2,
        brand="SecondBrand",
        model_name="Model-Y200",
        total_score=150.0,
    )
