from django.test import TestCase
from django_hosts import reverse

from util.test_utils import (
    CleanUpTempFilesTestMixin, Get, MOCK_JPG_FILE, assert_requesting_paths_succeeds, generate_all_admin_urls_for_model_and_objs,
)
from ..models import Equipment


class UrlTests(CleanUpTempFilesTestMixin, TestCase):

    def setUp(self):
        self.equipment1 = Equipment.objects.create(
            title="Test equipment 1",
            description="Lorem ipsum dolor sit amet",
            image=MOCK_JPG_FILE,
        )

    def test_all_get_request_paths_succeed(self):
        path_predicates = [
            Get(reverse('makerspace'), public=True),
            Get(reverse('makerspace_equipment_list'), public=True),
            Get(reverse('makerspace_admin_equipment_list'), public=False),
            Get(reverse('makerspace_equipment_create'), public=False),
            Get(reverse('makerspace_equipment_edit', args=[self.equipment1.pk]), public=False),
            Get(reverse('makerspace_equipment_detail', args=[self.equipment1.pk]), public=True),
            Get(reverse('rules'), public=True),
        ]
        assert_requesting_paths_succeeds(self, path_predicates)

    def test_all_admin_get_request_paths_succeed(self):
        path_predicates = [
            Get(admin_url, public=False)
            for admin_url in generate_all_admin_urls_for_model_and_objs(Equipment, [self.equipment1])
        ]
        assert_requesting_paths_succeeds(self, path_predicates, 'admin')
