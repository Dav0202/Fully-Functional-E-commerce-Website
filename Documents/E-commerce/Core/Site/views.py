import string
import random
import stripe
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, TemplateView
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Coupon, Item, OrderItem, Order, Address, Refund
from .forms import CheckoutForm, CouponForm, RefundForm


stripe.api_key = "sk_test_4eC39HqLyjWDarjtT1zdp7dc"


# Create your views here.
def is_vald_form(values):
    valid = True
    for firlds in values:
        if firlds == '':
            valid = False
    return valid


def create_reference_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=19))


def productpage(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "product-page.html", context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'form': form,
                'order': order,
                'couponform': CouponForm()
            }

            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("site:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)

            if form.is_valid():
                use_default_address = form.cleaned_data.get('save_info')
                if use_default_address:
                    print('Using default address')
                    address_qs = Address.objects.filter(
                        user=self.request.user,
                        default=True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shippping Available"
                        )
                        return redirect('site:checkout')
                else:
                    street_address = form.cleaned_data.get('street_address')
                    apartment_address = form.cleaned_data.get(
                        'apartment_address')
                    country = form.cleaned_data.get('country')
                    Zip = form.cleaned_data.get('Zip')
                    # same_shipping_address = form.cleaned_data.get('same_shipping_address')
                    # save_info = form.cleaned_data.get('save_info')

                    default = form.cleaned_data.get('default')
                    if is_vald_form([street_address, apartment_address, country, Zip]):
                        billing_address = Address(
                            user=self.request.user,
                            street_address=street_address,
                            apartment_address=apartment_address,
                            country=country,
                            Zip=Zip,
                            default=default
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                        set_default_shipping = form.cleaned_data.get('default')
                        if set_default_shipping:
                            billing_address.default = True
                            billing_address.save()
                    else:
                        messages.info(
                            self.request, "Please fill in required shiping address")

                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect('site:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('site:payment', payment_option='paypal')
                else:
                    messages.warning(self.request, "Invalid payment option")
                return redirect('site:checkout')
            messages.warning(self.request, "Failed CheckOut")
            return redirect('site:checkout')

        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active Order")
            return redirect("site:order-summary")


# class PaymentView(View):
#    def get(self, *args, **kwargs):
#        order = Order.objects.get(user=self.request.user, ordered=False)
#        context = {
#            'order': order
#        }
#        return render(self.request, "payment.html", context)
#
#    def post(self, *args, **kwargs):
#        order = Order.objects.get(user=self.request.user, ordered=False)
#        amount = int(order.get_total_price() * 100),  # cents
#        try:
#            charge = stripe.Charge.create(
#                amount=amount,
#                currency="usd",
#                description="My First Test Charge (created for API docs)",
#                source="tok_mastercard",
#            )
#            # create payment
#            payment = Payment()
#            payment.stripe_charge_id = charge['id']
#            payment.user = self.request.user
#            payment.amount = order.get_total_price()
#            payment.save()
#
#            # assign payment to order
#
#            order.ordered = True
#            order.payment = payment
#            order.save()
#
#            messages.success(self.request, "Your Order was Sucessful")
#            return redirect("/")
#
#        except stripe.error.CardError as e:
#            body = e.json_body
#            err = body.get('error', {})
#            messages.warning(self.request, f"{err.get('messages')}")
#            # Since it's a decline, stripe.error.CardError will be caught
#        except stripe.error.RateLimitError as e:
#            # Too many requests made to the API too quickly
#            messages.warning(self.request, "Rate Limit error")
#        except stripe.error.InvalidRequestError as e:
#            # Invalid parameters were supplied to Stripe's API
#            messages.warning(self.request, "Invalid parameter")
#        except stripe.error.AuthenticationError as e:
#            # Authentication with Stripe's API failed
#            # (maybe you changed API keys recently)
#            messages.warning(self.request, "Not auathenticated")
#        except stripe.error.APIConnectionError as e:
#            # Network communication with Stripe failed
#            messages.warning(self.request, "Network error")
#        except stripe.error.StripeError as e:
#            # Display a very generic error to the user, and maybe send
#            # yourself an email
#            messages.warning(self.request, "Some thing went wrong you were not charged")
#        except Exception as e:
#            # Send email to self
#            messages.warning(self.request, "Serious Error admin would be Notified")

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request, "You do not have a Billing Address")
        return redirect("Site:checkout")


class CreateCheckoutSessionView(View):
    def post(self, request, *args, **kwargs,):
        order = Order.objects.get(user=self.request.user, ordered=False)
        YOUR_DOMAIN = "http://127.0.0.1:8000/"
        # print(order.items)
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(order.get_total_price() * 100),
                        'product_data': {
                            'name': 'This is the Order'
                        }
                    },
                    'quantity': order.quantity,
                },
            ],
            payment_method_types=['card'],
            mode='payment',
            success_url=YOUR_DOMAIN + 'success/',
            cancel_url=YOUR_DOMAIN + 'cancel/',
        )
        order.ref_code = create_reference_code()
        order.ordered = True
        order.save()

        return redirect(checkout_session.url, code=303)


class SuccessView(TemplateView):
    template_name = "success.html"


class StripeIntentView(View):
    def post(self, request, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            intent = stripe.PaymentIntent.create(
                amount=int(order.get_total_price() * 100),
                currency='usd'
            )
            return JsonResponse({
                'clientSecret': intent['client_secret']
            })
        except Exception as e:
            return JsonResponse({'error': str(e)})


class HomeListView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by = 10


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, "order-summary.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active Order")
            return redirect("/")


class ProductDetailView(DetailView):
    model = Item
    template_name = "product-page.html"


def homepage(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "home-page.html", context)


@login_required
def add_to_cart(request, slug):

    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item,
                                                          user=request.user,
                                                          ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            print(created)
            messages.info(request, "This item quantity was updated")
        else:
            messages.info(request, "This item was added to cart")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to cart")
    return redirect("Site:productpage", slug=slug)


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,
                                    ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from the cart")
            return redirect("Site:order-summary")
        else:
            messages.info(request, "This item was not in the cart")
            return redirect("Site:productpage", slug=slug)
    else:
        messages.info(request, "You dont have an active order")
        return redirect("Site:productpage", slug=slug)


@login_required()
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user,
                                    ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item was quantity was Updated")
            return redirect("Site:order-summary")
        else:
            messages.info(request, "This item was not in the cart")
            return redirect("Site:productpage", slug=slug)
    else:
        messages.info(request, "You dont have an active order")
        return redirect("Site:productpage", slug=slug)


def add_single_item_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item,
                                                          user=request.user,
                                                          ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            print(created)
            messages.info(request, "This item quantity was updated")
            return redirect("Site:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to cart")
            return redirect("Site:order-summary")

    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to cart")
    return redirect("Site:order-summary")


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request, "This coupon does not exist")
        return redirect("Site:order-summary")


class AddCouponView(View):
    def post(self, request, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Sucesssfully added coupon")
                return redirect("Site:order-summary")

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an act8ve order")
                return redirect("Site:order-summary")


'''
def add_coupon(request):
    if request.method == "POST":
        form = CouponForm(request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=request.user, ordered=False)
                order.coupon = get_coupon(request, code)
                order.save()
                messages.success(request, "Sucesssfully added coupon")
                return redirect("Site:order-summary")

            except ObjectDoesNotExist:
                messages.info(request, "You do not have an act8ve order")
                return redirect("Site:order-summary")
    return None

'''


class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }

        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, "Your Request was recieved")
                return redirect("Site:request_refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist")
                return redirect("Site:request_refund")
