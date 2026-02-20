from django.contrib import admin, messages
from django.contrib.auth.models import User
from django import forms
from .models import Profile, Transaction

# ------------------------------
# Profile inline for users (your existing one)
# ------------------------------
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    readonly_fields = ('wallet_id',)  # prevent editing wallet ID
    verbose_name_plural = 'Wallet & Earnings'

class CustomUserAdmin(admin.ModelAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'is_staff')
    search_fields = ('username', 'email')

# ------------------------------
# Transaction admin (your existing one)
# ------------------------------
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'coin', 'amount', 'tx_type', 'status', 'created_at')
    list_filter = ('tx_type', 'coin', 'status')
    search_fields = ('user__username', 'coin')

# ------------------------------
# Custom form to add balance via wallet ID
# ------------------------------
class BalanceUpdateForm(forms.Form):
    wallet_id = forms.UUIDField(label="User Wallet ID")
    amount = forms.DecimalField(max_digits=12, decimal_places=2, label="Amount to Add")

# ------------------------------
# Profile admin (for wallet ID balance updates)
# ------------------------------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "wallet_id", "balance", "earnings")
    search_fields = ("user__username", "wallet_id")
    actions = ["add_balance_action"]

    def add_balance_action(self, request, queryset):
        form = None

        if "apply" in request.POST:
            form = BalanceUpdateForm(request.POST)
            if form.is_valid():
                wallet_id = form.cleaned_data["wallet_id"]
                amount = form.cleaned_data["amount"]
                try:
                    profile = Profile.objects.get(wallet_id=wallet_id)
                    profile.balance += amount
                    profile.save()
                    self.message_user(
                        request,
                        f"Successfully added ${amount} to {profile.user.username}'s balance.",
                        level=messages.SUCCESS
                    )
                except Profile.DoesNotExist:
                    self.message_user(
                        request,
                        "Wallet ID not found!",
                        level=messages.ERROR
                    )
                return None  # reload page

        if not form:
            form = BalanceUpdateForm()

        return admin.helpers.render_change_form(
            request,
            context={
                "form": form,
                "title": "Add Balance via Wallet ID",
                "opts": self.model._meta,
                "original": None,
            },
            add=True,
            change=False,
            form_url='',
            obj=None
        )

    add_balance_action.short_description = "Add balance using Wallet ID"

# ------------------------------
# Register users & transactions
# ------------------------------
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Transaction, TransactionAdmin)

