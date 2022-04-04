from http import HTTPStatus
from typing import List

from django.templatetags.static import static
from django.test import TestCase
from django.urls import reverse

from users.models import User
from ..utility import request_with_user
from ...forms import CreateMachineForm, EditMachineForm
from ...models.machine import Machine, MachineType
from ...views.reservation.machine import MachineListView


class TestMachineListView(TestCase):

    def setUp(self):
        self.printer_machine_type = MachineType.objects.get(pk=1)
        self.sewing_machine_type = MachineType.objects.get(pk=2)

    def test_no_machines(self):
        context_data = MachineListView.as_view()(request_with_user(None)).context_data
        self.assertIn('machine_types', context_data)
        self.assertFalse(context_data['machine_types'].exists())

    def test_one_type_of_machine(self):
        printer1 = Machine.objects.create(name="test1", machine_type=self.printer_machine_type)
        printer2 = Machine.objects.create(name="test2", machine_type=self.printer_machine_type)

        machine_types = list(MachineListView.as_view()(request_with_user(None)).context_data['machine_types'])
        self.assertEqual(len(machine_types), 1)
        machine_type_0 = machine_types[0]
        self.assertEqual(machine_type_0.pk, self.printer_machine_type.pk)
        self.assertEqual(machine_type_0.name, self.printer_machine_type.name)
        self.assertListEqual(list(machine_type_0.shown_machines), [printer1, printer2])

    def test_several_machine_types(self):
        printer1 = Machine.objects.create(name="test1", machine_type=self.printer_machine_type)
        printer2 = Machine.objects.create(name="test2", machine_type=self.printer_machine_type)
        sewing = Machine.objects.create(name="test", machine_type=self.sewing_machine_type)

        machine_types = list(MachineListView.as_view()(request_with_user(None)).context_data['machine_types'])
        self.assertEqual(len(machine_types), 2)
        machine_type_0, machine_type_1 = machine_types
        self.assertEqual(machine_type_0.pk, self.printer_machine_type.pk)
        self.assertEqual(machine_type_1.pk, self.sewing_machine_type.pk)
        self.assertEqual(machine_type_0.name, self.printer_machine_type.name)
        self.assertEqual(machine_type_1.name, self.sewing_machine_type.name)
        self.assertListEqual(list(machine_type_0.shown_machines), [printer1, printer2])
        self.assertListEqual(list(machine_type_1.shown_machines), [sewing])

    def test_internal_machines_are_only_shown_to_privileged_users(self):
        printer1 = Machine.objects.create(name="Printer 1", machine_type=self.printer_machine_type)
        printer2 = Machine.objects.create(name="Printer 2", machine_type=self.printer_machine_type)
        printer3_internal = Machine.objects.create(name="Printer 3", machine_type=self.printer_machine_type, internal=True)
        printer4 = Machine.objects.create(name="Printer 4", machine_type=self.printer_machine_type)
        sewing1_internal = Machine.objects.create(name="Sewing machine 1", machine_type=self.sewing_machine_type, internal=True)
        sewing2 = Machine.objects.create(name="Sewing machine 2", machine_type=self.sewing_machine_type)
        scanner1_internal = Machine.objects.create(name="Scanner 1", machine_type=MachineType.objects.get(pk=3), internal=True)

        machine_list_url = reverse('machine_list')

        def assert_machine_list_contains(expected_machines_per_machine_type: List[List[Machine]]):
            response = self.client.get(machine_list_url)
            self.assertEqual(response.status_code, HTTPStatus.OK)
            # Filter the machine types the same way as in the template
            machine_types = list(machine_type for machine_type in response.context['machine_types'] if machine_type.shown_machines)
            self.assertEqual(len(machine_types), len(expected_machines_per_machine_type))
            for machine_type, expected_machines in zip(machine_types, expected_machines_per_machine_type):
                self.assertListEqual(list(machine_type.shown_machines), expected_machines)

        # The internal machines should not be shown to anonymous users
        assert_machine_list_contains([
            [printer1, printer2, printer4],
            [sewing2],
        ])

        # The internal machines should not be shown to unprivileged users
        user = User.objects.create_user("user1")
        self.client.force_login(user)
        assert_machine_list_contains([
            [printer1, printer2, printer4],
            [sewing2],
        ])

        # The internal machines should be shown to MAKE members
        user.add_perms('internal.is_internal')
        assert_machine_list_contains([
            [printer1, printer2, printer3_internal, printer4],
            [sewing1_internal, sewing2],
            [scanner1_internal],
        ])

    def test_machines_are_sorted_correctly(self):
        correct_machine_orders = []
        for machine_type in (self.printer_machine_type, self.sewing_machine_type):
            machine_b = self.create_machine("b", machine_type)
            machine_c = self.create_machine("c", machine_type)
            machine_d = self.create_machine("d", machine_type)
            machine_1_h = self.create_machine("h", machine_type, priority=1)
            machine_3_e = self.create_machine("e", machine_type, priority=3)
            machine_2_f = self.create_machine("f", machine_type, priority=2)
            machine_2_g = self.create_machine("g", machine_type, priority=2)
            machine_2_a = self.create_machine("a", machine_type, priority=2)
            correct_machine_orders.append([
                machine_1_h,
                machine_2_a, machine_2_f, machine_2_g,
                machine_3_e,
                machine_b, machine_c, machine_d,
            ])

        machine_types = list(MachineListView.as_view()(request_with_user(None)).context_data['machine_types'])
        for machine_type, correct_machine_order in zip(machine_types, correct_machine_orders):
            with self.subTest(machine_type=machine_type):
                self.assertListEqual(list(machine_type.shown_machines), correct_machine_order)

    def test_get_machine_list_view_contains_img_path_in_html(self):
        def assert_response_contains_num_of_each_img_path(num_of_each: int):
            response = self.client.get(reverse('machine_list'))
            for stream_image_name in ['out_of_order', 'no_stream', 'maintenance']:
                with self.subTest(stream_image_name=stream_image_name):
                    self.assertContains(response, static(f'make_queue/img/{stream_image_name}.svg'), count=num_of_each)

        assert_response_contains_num_of_each_img_path(0)

        self.create_machine(name_prefix="available", machine_type=self.printer_machine_type, status=Machine.Status.AVAILABLE)
        self.create_machine(name_prefix="out of order", machine_type=self.printer_machine_type, status=Machine.Status.OUT_OF_ORDER)
        self.create_machine(name_prefix="maintenance", machine_type=self.printer_machine_type, status=Machine.Status.MAINTENANCE)

        assert_response_contains_num_of_each_img_path(1)

    @staticmethod
    def create_machine(name_prefix: str, machine_type: MachineType, **kwargs) -> Machine:
        """Creates a machine of type ``machine_type`` with name '``name_prefix`` ``machine_type``'."""
        return Machine.objects.create(
            name=f"{name_prefix} {machine_type.name}",
            machine_type=machine_type,
            **kwargs,
        )


class TestMachineDetailView(TestCase):

    def test_only_internal_users_can_view_internal_machines(self):
        for machine_type in MachineType.objects.all():
            with self.subTest(machine_type=machine_type):
                user = User.objects.create_user(username=f"user{machine_type.pk}")
                self.client.force_login(user)

                machine = Machine.objects.create(name=f"{machine_type} 1", machine_type=machine_type)
                machine_detail_url = reverse('machine_detail', args=[2022, 1, machine.pk])

                # User should be allowed when machine is not internal
                response = self.client.get(machine_detail_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

                # User should not be able to find the machine when it's internal
                machine.internal = True
                machine.save()
                response = self.client.get(machine_detail_url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

                # User should be allowed when they're internal
                user.add_perms('internal.is_internal')
                response = self.client.get(machine_detail_url)
                self.assertEqual(response.status_code, HTTPStatus.OK)


class TestCreateAndEditMachineView(TestCase):

    def setUp(self):
        username = "TEST_USER"
        password = "TEST_PASS"
        self.user = User.objects.create_user(username=username, password=password)
        self.user.add_perms('make_queue.add_machine', 'make_queue.change_machine')
        self.client.login(username=username, password=password)

    def test_edit_machine_context_data_has_correct_form(self):
        printer_machine_type = MachineType.objects.get(pk=1)
        machine = Machine.objects.create(
            name="Test",
            machine_model="Ultimaker 2+",
            machine_type=printer_machine_type,
        )
        response = self.client.get(reverse('edit_machine', args=[machine.pk]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(isinstance(response.context_data['form'], EditMachineForm))

    def test_create_machine_context_data_has_correct_form(self):
        response = self.client.get(reverse('create_machine'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(isinstance(response.context_data['form'], CreateMachineForm))
