from django.test import TestCase
from django.utils import timezone
from shopping.models import ShoppingList, ShoppingItem, ItemPrice, Quote

class ShoppingListTestCase(TestCase):
    def setUp(self):
        self.shopping_list = ShoppingList.objects.create(
            customer_email="test@example.com",
            customer_phone="256700000000",
            delivery_address="Test Address",
            special_instructions="Leave at the front door"
        )

    def test_soft_delete(self):
        self.shopping_list.soft_delete()
        self.assertFalse(self.shopping_list.is_active)
        self.assertIsNotNone(self.shopping_list.deleted_at)

    def test_unarchive(self):
        self.shopping_list.soft_delete()
        self.shopping_list.unarchive()
        self.assertTrue(self.shopping_list.is_active)
        self.assertIsNone(self.shopping_list.deleted_at)

    def test_string_representation(self):
        self.assertEqual(str(self.shopping_list), f"List {self.shopping_list.id} - submitted")


class ShoppingItemTestCase(TestCase):
    def setUp(self):
        self.shopping_list = ShoppingList.objects.create(
            customer_email="test@example.com",
            customer_phone="256700000000",
            delivery_address="Test Address"
        )
        self.item = ShoppingItem.objects.create(
            shopping_list=self.shopping_list,
            name="Sugar",
            quantity="2 kg",
            description="White refined sugar"
        )
        self.item_price = ItemPrice.objects.create(
            name="Sugar",
            current_price=7000
        )

    def test_string_representation(self):
        self.assertEqual(str(self.item), "Sugar (2 kg)")

    def test_suggest_price(self):
        suggested_price = self.item.suggest_price()
        self.assertEqual(suggested_price, 7000)

    def test_suggest_price_no_price_available(self):
        new_item = ShoppingItem.objects.create(
            shopping_list=self.shopping_list,
            name="Flour",
            quantity="1 kg",
        )
        self.assertIsNone(new_item.suggest_price())


class ItemPriceTestCase(TestCase):
    def setUp(self):
        self.price_record = ItemPrice.objects.create(
            name="Sugar",
            current_price=8000
        )

    def test_string_representation(self):
        self.assertEqual(str(self.price_record), "Sugar - 8000")

    def test_price_updates(self):
        self.price_record.current_price = 8500
        self.price_record.save()
        self.assertEqual(self.price_record.current_price, 8500)
        self.assertTrue(timezone.now() >= self.price_record.last_updated)


class QuoteTestCase(TestCase):
    def setUp(self):
        self.shopping_list = ShoppingList.objects.create(
            customer_email="test@example.com",
            customer_phone="256700000000",
            delivery_address="Test Address"
        )
        self.quote = Quote.objects.create(
            shopping_list=self.shopping_list,
            expires_at=timezone.now() + timezone.timedelta(days=3),
            subtotal=100000,
            delivery_fee=5000,
            service_fee=2000,
            total=107000
        )

    def test_string_representation(self):
        self.assertEqual(str(self.quote), f"Quote for List {self.shopping_list.id}")

    def test_soft_delete(self):
        self.quote.soft_delete()
        self.assertFalse(self.quote.is_active)
        self.assertIsNotNone(self.quote.deleted_at)

    def test_unarchive(self):
        self.quote.soft_delete()
        self.quote.unarchive()
        self.assertTrue(self.quote.is_active)
        self.assertIsNone(self.quote.deleted_at)

    def test_total_calculation(self):
        self.quote.subtotal = 100000
        self.quote.delivery_fee = 5000
        self.quote.service_fee = 2000
        self.quote.save()
        self.assertEqual(self.quote.total, 107000)
