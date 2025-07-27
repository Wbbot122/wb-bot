import os
from dataclasses import dataclass

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Router

from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

@dataclass
class ItemCalc:
    name: str
    cost: float
    delivery_to_wb: float
    packaging: float
    fulfillment: float
    mp_price_before_discount: float
    discount_coeff: float
    buyout_percent: float
    wb_commission_percent: float
    mp_logistics_to_pvz: float
    return_cost_per_unit: float
    marketing_internal: float
    marketing_external: float
    photos: float

    def compute(self):
        buyout = self.buyout_percent / 100.0
        price_after_discount = self.mp_price_before_discount * self.discount_coeff
        commission_rub_sold = price_after_discount * (self.wb_commission_percent / 100.0)
        expected_return_cost = (1 - buyout) * self.return_cost_per_unit

        base_costs_per_unit = (
            self.cost + self.delivery_to_wb + self.packaging + self.fulfillment +
            self.marketing_internal + self.marketing_external + self.photos +
            self.mp_logistics_to_pvz + expected_return_cost
        )

        if buyout > 0:
            redistributed_return_cost_per_sold = expected_return_cost / buyout
        else:
            redistributed_return_cost_per_sold = 0

        costs_per_sold = (
            self.cost + self.delivery_to_wb + self.packaging + self.fulfillment +
            self.marketing_internal + self.marketing_external + self.photos +
            self.mp_logistics_to_pvz + redistributed_return_cost_per_sold +
            commission_rub_sold
        )

        profit_per_sold = price_after_discount - costs_per_sold
        roi_per_sold = profit_per_sold / (self.cost if self.cost else 1)

        expected_revenue_per_unit = price_after_discount * buyout
        expected_commission_per_unit = commission_rub_sold * buyout
        expected_profit_per_unit = expected_revenue_per_unit - (
            base_costs_per_unit + expected_commission_per_unit
        )
        roi_expected = expected_profit_per_unit / (self.cost if self.cost else 1)

        return {
            "price_after_discount": price_after_discount,
            "commission_rub_sold": commission_rub_sold,
            "expected_return_cost": expected_return_cost,
            "profit_per_sold": profit_per_sold,
            "roi_per_sold": roi_per_sold,
            "expected_profit_per_unit": expected_profit_per_unit,
            "roi_expected": roi_expected,
            "expected_revenue_per_unit": expected_revenue_per_unit,
            "costs_per_sold": costs_per_sold,
            "base_costs_per_unit": base_costs_per_unit,
        }

class CalcForm(StatesGroup):
    name = State()
    cost = State()
    delivery_to_wb = State()
    packaging = State()
    fulfillment = State()
    mp_price_before_discount = State()
    discount_coeff = State()
    buyout_percent = State()
    wb_commission_percent = State()
    mp_logistics_to_pvz = State()
    return_cost_per_unit = State()
    marketing_internal = State()
    marketing_external = State()
    photos = State()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await message.answer("Привет! Напиши /calc чтобы начать расчёт.")
    await state.clear()

@router.message(Command("calc"))
async def start_calc(message: Message, state: FSMContext):
    await message.answer("1) Название товара:")
    await state.set_state(CalcForm.name)

@router.message(CalcForm.name)
async def s1(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("2) Себестоимость:")
    await state.set_state(CalcForm.cost)

@router.message(CalcForm.cost)
async def s2(message: Message, state: FSMContext):
    await state.update_data(cost=float(message.text.replace(",", ".")))
    await message.answer("3) Доставка до WB:")
    await state.set_state(CalcForm.delivery_to_wb)

@router.message(CalcForm.delivery_to_wb)
async def s3(message: Message, state: FSMContext):
    await state.update_data(delivery_to_wb=float(message.text.replace(",", ".")))
    await message.answer("4) Упаковка:")
    await state.set_state(CalcForm.packaging)

@router.message(CalcForm.packaging)
async def s4(message: Message, state: FSMContext):
    await state.update_data(packaging=float(message.text.replace(",", ".")))
    await message.answer("5) Фулфилмент:")
    await state.set_state(CalcForm.fulfillment)

@router.message(CalcForm.fulfillment)
async def s5(message: Message, state: FSMContext):
    await state.update_data(fulfillment=float(message.text.replace(",", ".")))
    await message.answer("6) Цена до скидки:")
    await state.set_state(CalcForm.mp_price_before_discount)

@router.message(CalcForm.mp_price_before_discount)
async def s6(message: Message, state: FSMContext):
    await state.update_data(mp_price_before_discount=float(message.text.replace(",", ".")))
    await message.answer("7) Скидка (например 0.75):")
    await state.set_state(CalcForm.discount_coeff)

@router.message(CalcForm.discount_coeff)
async def s7(message: Message, state: FSMContext):
    await state.update_data(discount_coeff=float(message.text.replace(",", ".")))
    await message.answer("8) Процент выкупа:")
    await state.set_state(CalcForm.buyout_percent)

@router.message(CalcForm.buyout_percent)
async def s8(message: Message, state: FSMContext):
    await state.update_data(buyout_percent=float(message.text.replace(",", ".")))
    await message.answer("9) Комиссия WB (%):")
    await state.set_state(CalcForm.wb_commission_percent)

@router.message(CalcForm.wb_commission_percent)
async def s9(message: Message, state: FSMContext):
    await state.update_data(wb_commission_percent=float(message.text.replace(",", ".")))
    await message.answer("10) Логистика до ПВЗ:")
    await state.set_state(CalcForm.mp_logistics_to_pvz)

@router.message(CalcForm.mp_logistics_to_pvz)
async def s10(message: Message, state: FSMContext):
    await state.update_data(mp_logistics_to_pvz=float(message.text.replace(",", ".")))
    await message.answer("11) Стоимость возврата:")
    await state.set_state(CalcForm.return_cost_per_unit)

@router.message(CalcForm.return_cost_per_unit)
async def s11(message: Message, state: FSMContext):
    await state.update_data(return_cost_per_unit=float(message.text.replace(",", ".")))
    await message.answer("12) Внутренний маркетинг:")
    await state.set_state(CalcForm.marketing_internal)

@router.message(CalcForm.marketing_internal)
async def s12(message: Message, state: FSMContext):
    await state.update_data(marketing_internal=float(message.text.replace(",", ".")))
    await message.answer("13) Внешний маркетинг:")
    await state.set_state(CalcForm.marketing_external)

@router.message(CalcForm.marketing_external)
async def s13(message: Message, state: FSMContext):
    await state.update_data(marketing_external=float(message.text.replace(",", ".")))
    await message.answer("14) Фотосессия:")
    await state.set_state(CalcForm.photos)

@router.message(CalcForm.photos)
async def s14(message: Message, state: FSMContext):
    await state.update_data(photos=float(message.text.replace(",", ".")))
    data = await state.get_data()
    item = ItemCalc(**data)
    result = item.compute()

    text = (
        f"🔎 Товар: {item.name}\n"
        f"💰 Цена после скидки: {result['price_after_discount']:.2f} ₽\n"
        f"📉 Комиссия WB: {result['commission_rub_sold']:.2f} ₽\n"
        f"🔁 Возвраты (на единицу): {result['expected_return_cost']:.2f} ₽\n\n"
        f"📦 На 1 проданную:\n"
        f"• Прибыль: {result['profit_per_sold']:.2f} ₽\n"
        f"• ROI: {result['roi_per_sold']*100:.2f}%\n\n"
        f"📊 На 1 отгруженную:\n"
        f"• Ожидаемая прибыль: {result['expected_profit_per_unit']:.2f} ₽\n"
        f"• ROI (ожидаемо): {result['roi_expected']*100:.2f}%"
    )
    await message.answer(text)
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
