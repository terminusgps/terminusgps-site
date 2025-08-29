from django.contrib import admin, messages
from django.utils.translation import ngettext

from terminusgps_tracker.models import (
    Customer,
    CustomerPaymentMethod,
    CustomerShippingAddress,
    CustomerSubscription,
    CustomerSubscriptionTier,
    CustomerWialonUnit,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    actions = [
        "authorizenet_sync_payment_methods",
        "authorizenet_sync_shipping_addresses",
    ]
    list_display = [
        "id",
        "user",
        "authorizenet_profile_id",
        "wialon_resource_id",
        "wialon_user_id",
    ]

    @admin.action(
        description="Sync selected customer payment methods from Authorizenet"
    )
    def authorizenet_sync_payment_methods(self, request, queryset):
        for customer in queryset:
            response = customer.get_authorizenet_profile()
            if response is not None and all(
                [
                    hasattr(response, "profile"),
                    hasattr(response.profile, "paymentProfiles"),
                ]
            ):
                local_payment_ids = list(
                    CustomerPaymentMethod.objects.filter(
                        customer=customer
                    ).values_list("id", flat=True)
                )
                remote_payment_ids = [
                    int(paymentProfile.customerPaymentProfileId)
                    for paymentProfile in response.profile.paymentProfiles
                ]
                ids_to_create = (
                    set(remote_payment_ids) - set(local_payment_ids)
                    if remote_payment_ids
                    else None
                )
                ids_to_delete = (
                    set(local_payment_ids) - set(remote_payment_ids)
                    if local_payment_ids
                    else None
                )

                if ids_to_create:
                    CustomerPaymentMethod.objects.bulk_create(
                        [
                            CustomerPaymentMethod(id=id, customer=customer)
                            for id in ids_to_create
                        ],
                        ignore_conflicts=True,
                    )
                if ids_to_delete:
                    CustomerPaymentMethod.objects.filter(
                        id__in=ids_to_delete
                    ).delete()

            self.message_user(
                request,
                ngettext(
                    "%d customer had its payment methods synced with Authorizenet.",
                    "%d customers had their payment methods synced with Authorizenet.",
                    len(queryset),
                )
                % len(queryset),
                messages.SUCCESS,
            )

    @admin.action(
        description="Sync selected customer shipping addresses from Authorizenet"
    )
    def authorizenet_sync_shipping_addresses(self, request, queryset):
        for customer in queryset:
            response = customer.get_authorizenet_profile()
            if response is not None and all(
                [
                    hasattr(response, "profile"),
                    hasattr(response.profile, "shipToList"),
                ]
            ):
                local_address_ids = list(
                    CustomerShippingAddress.objects.filter(
                        customer=customer
                    ).values_list("id", flat=True)
                )
                remote_address_ids = [
                    int(addressProfile.customerAddressId)
                    for addressProfile in response.profile.shipToList
                ]
                ids_to_create = (
                    set(remote_address_ids) - set(local_address_ids)
                    if remote_address_ids
                    else None
                )
                ids_to_delete = (
                    set(local_address_ids) - set(remote_address_ids)
                    if local_address_ids
                    else None
                )

                if ids_to_create:
                    CustomerShippingAddress.objects.bulk_create(
                        [
                            CustomerShippingAddress(id=id, customer=customer)
                            for id in ids_to_create
                        ],
                        ignore_conflicts=True,
                    )
                if ids_to_delete:
                    CustomerShippingAddress.objects.filter(
                        id__in=ids_to_delete
                    ).delete()

            self.message_user(
                request,
                ngettext(
                    "%d customer had its shipping addresses synced with Authorizenet.",
                    "%d customers had their shipping addresses synced with Authorizenet.",
                    len(queryset),
                )
                % len(queryset),
                messages.SUCCESS,
            )


@admin.register(CustomerWialonUnit)
class CustomerWialonUnitAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "tier", "customer"]
    list_filter = ["tier"]


@admin.register(CustomerPaymentMethod)
class CustomerPaymentMethodAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]


@admin.register(CustomerShippingAddress)
class CustomerShippingAddressAdmin(admin.ModelAdmin):
    list_display = ["id", "customer"]


@admin.register(CustomerSubscription)
class CustomerSubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "customer", "status"]
    list_filter = ["status"]


@admin.register(CustomerSubscriptionTier)
class CustomerSubscriptionTierAdmin(admin.ModelAdmin):
    list_display = ["name", "price"]
