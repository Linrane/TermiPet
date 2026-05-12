"""测试共享 fixtures"""
import sys
import os

# 确保 src 目录在 Python 路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from termipet.database import Base
from termipet.utils.seeds import seed_data, SPECIES_DATA, ITEMS_DATA
from termipet.models.pet import Pet, Species
from termipet.models.item import Item
from termipet.models.home import Home


@pytest.fixture(scope="function")
def engine():
    """内存 SQLite 引擎（每个测试独立）"""
    e = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}
    )
    # 导入所有模型以注册它们
    from termipet.models import (
        pet, item, home, skill, quest, maze, story, daily_event
    )
    Base.metadata.create_all(e)
    return e


@pytest.fixture(scope="function")
def Session(engine):
    return sessionmaker(bind=engine)


@pytest.fixture(scope="function")
def db_session(Session):
    """带自动种子数据的 session"""
    session = Session()

    # 插入物种数据
    for data in SPECIES_DATA:
        if not session.query(Species).filter_by(key=data["key"]).first():
            species = Species(**{k: v for k, v in data.items()})
            session.add(species)

    # 插入物品数据
    for data in ITEMS_DATA:
        if not session.query(Item).filter_by(key=data["key"]).first():
            item = Item(**{k: v for k, v in data.items()})
            session.add(item)

    session.commit()
    yield session
    session.close()


@pytest.fixture
def sample_pet(db_session):
    """创建一个基础测试宠物（非蛋期，方便测试各种操作）"""
    from termipet.core.pet_manager import PetManager
    pm = PetManager(db_session)
    pet = pm.adopt(species_key="cat", name="测试喵")
    # 手动设置为少年期以便测试更多功能
    pet.stage = "少年"
    pet.age_days = 10.0
    pet.hunger = 60.0
    pet.happiness = 60.0
    pet.energy = 60.0
    pet.health = 60.0
    pet.cleanliness = 60.0
    pet.coins = 500
    db_session.commit()
    return pet


@pytest.fixture
def egg_pet(db_session):
    """创建一个蛋期宠物"""
    from termipet.core.pet_manager import PetManager
    pm = PetManager(db_session)
    pet = pm.adopt(species_key="dog", name="测试蛋")
    # 保持蛋期状态
    assert pet.stage == "蛋"
    return pet


@pytest.fixture
def dog_pet(db_session):
    """创建一个犬型宠物"""
    from termipet.core.pet_manager import PetManager
    pm = PetManager(db_session)
    pet = pm.adopt(species_key="dog", name="测试犬")
    pet.stage = "少年"
    pet.age_days = 10.0
    pet.hunger = 60.0
    pet.happiness = 60.0
    pet.energy = 60.0
    pet.health = 60.0
    pet.cleanliness = 60.0
    pet.coins = 500
    db_session.commit()
    return pet


@pytest.fixture
def bird_pet(db_session):
    """创建一个鸟型宠物"""
    from termipet.core.pet_manager import PetManager
    pm = PetManager(db_session)
    pet = pm.adopt(species_key="bird", name="测试鸟")
    pet.stage = "少年"
    pet.age_days = 10.0
    pet.hunger = 60.0
    pet.happiness = 60.0
    pet.energy = 60.0
    pet.health = 60.0
    pet.cleanliness = 60.0
    pet.coins = 500
    db_session.commit()
    return pet


@pytest.fixture
def pet_with_materials(db_session, sample_pet):
    """创建有材料的宠物（用于制作系统测试）"""
    # 添加材料到背包
    from termipet.models.item import Item, Inventory

    materials = [
        ("raw_fish", 5),
        ("seasoning", 3),
        ("herb", 5),
        ("water", 3),
        ("iron_ingot", 5),
        ("leather", 3),
        ("paper", 10),
        ("ink", 5),
        ("data_shard", 2),
    ]

    for item_key, qty in materials:
        item = db_session.query(Item).filter_by(key=item_key).first()
        assert item is not None, f"Item {item_key} not found"
        inv = Inventory(pet_id=sample_pet.id, item_id=item.id, quantity=qty)
        db_session.add(inv)

    db_session.commit()
    return sample_pet


@pytest.fixture
def pet_with_home_upgraded(db_session, sample_pet):
    """创建有升级房间的宠物"""
    from termipet.models.home import Home

    home = db_session.query(Home).filter_by(pet_id=sample_pet.id).first()
    assert home is not None
    home.kitchen_level = 3
    home.workshop_level = 2
    home.library_level = 1
    db_session.commit()
    return sample_pet
