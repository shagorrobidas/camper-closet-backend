from django.core.management.base import BaseCommand
from packing.models import PackingTemplate, PackingTemplateCategory, PackingTemplateItem, TripType
from closet.models import ItemCategoryType

class Command(BaseCommand):
    help = 'Seed the full CAMP WAYNE FOR GIRLS 2026 packing template from the official list'

    def handle(self, *args, **options):
        self.stdout.write('Seeding CAMP WAYNE FOR GIRLS 2026 Full List...')

        # Delete old version if it exists to avoid duplication
        PackingTemplate.objects.filter(title='CAMP WAYNE FOR GIRLS 2026').delete()

        # Ensure a TripType exists
        trip_type, _ = TripType.objects.get_or_create(
            name='Summer Camp',
            defaults={'description': 'Summer camp packing list'}
        )

        # Common ItemCategoryTypes
        clothing_type = ItemCategoryType.objects.filter(name__icontains='Clothing').first()
        shoes_type = ItemCategoryType.objects.filter(name__icontains='Shoes').first()
        toiletries_type = ItemCategoryType.objects.filter(name__icontains='Toiletries').first()

        # Create Template
        template = PackingTemplate.objects.create(
            title='CAMP WAYNE FOR GIRLS 2026',
            trip_type=trip_type,
            season='Summer',
            description='Official 2026 Packing List for Camp Wayne for Girls.',
            is_system=True,
            sort_order=1
        )

        # Full Data from Image
        data = [
            {
                'name': 'REQUIRED CAMP WAYNE UNIFORM',
                'items': [
                    {'title': 'CWG Uniform T-shirt (for picture day and trips)', 'qty': 1, 'is_required': True},
                    {'title': 'CWG Reversible Mesh Pinny (for tournaments & Color War)', 'qty': 1, 'is_required': True},
                    {'title': 'CWG Shorts – NEW style and logo', 'qty': 1, 'is_required': True},
                ]
            },
            {
                'name': 'SUGGESTED CAMP WAYNE CLOTHING',
                'items': [
                    {'title': 'CWG Blue T-Shirts', 'qty': 2, 'is_required': False},
                    {'title': 'CWG White T-Shirts', 'qty': 2, 'is_required': False},
                    {'title': 'CWG Sweatshirt', 'qty': 1, 'is_required': False},
                    {'title': 'CWG Sweatpants', 'qty': 1, 'is_required': False},
                ]
            },
            {
                'name': 'ADDITIONAL CLOTHING',
                'items': [
                    {'title': 'T-Shirts/Tank Tops for daytime', 'qty': 10, 'is_required': False},
                    {'title': 'T-Shirts/Tank Tops for nighttime', 'qty': 5, 'is_required': False},
                    {'title': 'Long Sleeve Shirts', 'qty': 4, 'is_required': False},
                    {'title': 'Sweatshirts', 'qty': 3, 'is_required': False},
                    {'title': 'Shorts for daytime', 'qty': 10, 'is_required': False},
                    {'title': 'Shorts for nighttime', 'qty': 5, 'is_required': False},
                    {'title': 'Sweatpants', 'qty': 4, 'is_required': False},
                    {'title': 'Black Leggings', 'qty': 1, 'is_required': False},
                    {'title': 'Leggings/Jeans', 'qty': 4, 'is_required': False},
                    {'title': 'Hat/Visor', 'qty': 1, 'is_required': False},
                    {'title': 'Dressier Outfits for Discos (e.g., skirt)', 'qty': 2, 'is_required': False},
                    {'title': '100% Cotton Clothing for MADD (white/dark for bleaching)', 'qty': 3, 'is_required': False},
                    {'title': 'Spirit Wear (Color War, 4th of July, etc.)', 'qty': 1, 'is_required': False},
                    {'title': 'Theme Disco Outfit', 'qty': 1, 'is_required': False},
                    {'title': 'Group Dance & Cheer Outfit', 'qty': 1, 'is_required': False},
                ]
            },
            {
                'name': 'OUTERWEAR',
                'items': [
                    {'title': 'Warm Jacket/Fleece', 'qty': 1, 'is_required': False},
                    {'title': 'Hooded Rain Coat or Poncho', 'qty': 1, 'is_required': True},
                ]
            },
            {
                'name': 'FOOTWEAR',
                'items': [
                    {'title': 'Sneakers WITH LACES', 'qty': 2, 'is_required': True},
                    {'title': 'Flip Flops/WaterSlides/CROCS', 'qty': 2, 'is_required': False},
                    {'title': 'Sandals/Nice Flip Flops', 'qty': 2, 'is_required': False},
                    {'title': 'Waterproof Shoes/Rain Boots', 'qty': 1, 'is_required': True},
                    {'title': 'Cleats', 'qty': 1, 'is_required': True},
                    {'title': 'Flip Flops for Shower use', 'qty': 1, 'is_required': False},
                    {'title': 'Slippers', 'qty': 1, 'is_required': False},
                ]
            },
            {
                'name': 'UNDERWEAR, SOCKS, SWIMWEAR',
                'items': [
                    {'title': 'Underwear', 'qty': 20, 'is_required': False},
                    {'title': 'Leotard for Gymnastics', 'qty': 1, 'is_required': True},
                    {'title': 'Bras/Sports Bras', 'qty': 5, 'is_required': False},
                    {'title': 'White sports bra/layering tank for under pinny', 'qty': 1, 'is_required': False},
                    {'title': 'Socks', 'qty': 20, 'is_required': False},
                    {'title': 'Soccer Socks', 'qty': 2, 'is_required': False},
                    {'title': 'Swimsuits', 'qty': 6, 'is_required': False},
                ]
            },
            {
                'name': 'SLEEPWEAR',
                'items': [
                    {'title': 'Lightweight Sleepwear Sets', 'qty': 4, 'is_required': False},
                    {'title': 'Heavyweight Sleepwear Sets', 'qty': 4, 'is_required': False},
                    {'title': 'Pajama Pants', 'qty': 2, 'is_required': False},
                ]
            },
            {
                'name': 'BEDDING/LAUNDRY',
                'items': [
                    {'title': 'Twin or Twin XL Sheet Sets', 'qty': 2, 'is_required': True},
                    {'title': 'Lightweight Comforter', 'qty': 1, 'is_required': True},
                    {'title': 'Warm Blanket (e.g., fleece)', 'qty': 1, 'is_required': False},
                    {'title': 'Small Throw Blanket', 'qty': 1, 'is_required': False},
                    {'title': 'Pillow', 'qty': 1, 'is_required': True},
                    {'title': 'Mattress Pad', 'qty': 1, 'is_required': False},
                    {'title': 'Mattress Topper (Egg Crate/Memory Foam)', 'qty': 1, 'is_required': False},
                    {'title': 'Stain Stick', 'qty': 1, 'is_required': False},
                    {'title': 'Small Open Bins/Mesh bags for socks/underwear', 'qty': 2, 'is_required': False},
                ]
            },
            {
                'name': 'LABELING',
                'items': [
                    {'title': 'Sew-on / Iron-on / Stick-on Name Labels', 'qty': 1, 'is_required': True},
                    {'title': 'Equipment Stickers', 'qty': 1, 'is_required': True},
                ]
            },
            {
                'name': 'BATH/TOILETRIES',
                'items': [
                    {'title': 'Bath Towels', 'qty': 6, 'is_required': True},
                    {'title': 'Wash Cloths', 'qty': 1, 'is_required': False},
                    {'title': 'Shower Caddy', 'qty': 1, 'is_required': True},
                    {'title': 'Brushes', 'qty': 2, 'is_required': True},
                    {'title': 'Wide Tooth Comb', 'qty': 1, 'is_required': False},
                    {'title': 'Hairbands, Hair Ties, Hair Accessories', 'qty': 1, 'is_required': False},
                    {'title': 'Toothbrush, Toothpaste, Toothbrush Holder', 'qty': 1, 'is_required': True},
                    {'title': 'Soap (liquid, foam, or bar w/case)', 'qty': 1, 'is_required': True},
                    {'title': 'Shampoo & Conditioner & Detangler', 'qty': 1, 'is_required': True},
                    {'title': 'Lice Repellent Shampoo & Conditioner & Spray', 'qty': 1, 'is_required': False},
                    {'title': 'Drinking Cup', 'qty': 1, 'is_required': False},
                    {'title': 'Qtips', 'qty': 1, 'is_required': False},
                    {'title': 'Deodorant', 'qty': 1, 'is_required': False},
                    {'title': 'Feminine Products', 'qty': 1, 'is_required': False},
                    {'title': 'Razors/Shaving Cream', 'qty': 1, 'is_required': False},
                    {'title': 'Box of Tissues', 'qty': 1, 'is_required': True},
                    {'title': 'Nail Clippers', 'qty': 1, 'is_required': True},
                    {'title': 'Insect Repellent', 'qty': 1, 'is_required': False},
                    {'title': 'Aerosol Sunscreen', 'qty': 2, 'is_required': True},
                    {'title': 'Sunscreen Face Sticks', 'qty': 2, 'is_required': True},
                ]
            },
            {
                'name': 'PACKING & CAMP GEAR',
                'items': [
                    {'title': 'Camp Chair (e.g., Crazy Creek)', 'qty': 1, 'is_required': True},
                    {'title': 'Large Duffels', 'qty': 2, 'is_required': False},
                    {'title': 'Drawstring Backpack', 'qty': 1, 'is_required': True},
                    {'title': 'Big Trip Overnight Bag (6th grade+)', 'qty': 1, 'is_required': True},
                    {'title': 'Fanny Pack', 'qty': 1, 'is_required': False},
                ]
            },
            {
                'name': 'SPORTS EQUIPMENT',
                'items': [
                    {'title': 'Soccer Shin Guards', 'qty': 1, 'is_required': True},
                    {'title': 'Softball Glove', 'qty': 1, 'is_required': True},
                    {'title': 'Tennis Racket', 'qty': 1, 'is_required': True},
                    {'title': 'Can of Tennis Balls', 'qty': 1, 'is_required': False},
                    {'title': 'Swim Goggles', 'qty': 1, 'is_required': False},
                ]
            },
            {
                'name': 'ESSENTIALS',
                'items': [
                    {'title': 'Wide-Mouthed Water Bottles (no straws)', 'qty': 2, 'is_required': True},
                    {'title': 'Flashlight with Extra Batteries', 'qty': 1, 'is_required': True},
                    {'title': 'Battery Operated Fan w/Extra Batteries', 'qty': 1, 'is_required': True},
                    {'title': 'Water Misting Fan', 'qty': 1, 'is_required': False},
                    {'title': 'Stationery, Stamps, Pens/Pencils', 'qty': 1, 'is_required': False},
                ]
            }
        ]

        for i, cat_data in enumerate(data):
            category = PackingTemplateCategory.objects.create(
                template=template,
                name=cat_data['name'],
                sort_order=i
            )
            for j, item_data in enumerate(cat_data['items']):
                PackingTemplateItem.objects.create(
                    template=template,
                    category=category,
                    title=item_data['title'],
                    quantity=item_data['qty'],
                    is_required=item_data.get('is_required', False),
                    sort_order=j
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded template "{template.title}" with {len(data)} categories and dozens of items.'))
