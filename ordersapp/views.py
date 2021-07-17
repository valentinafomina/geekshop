from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.forms import inlineformset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from basketapp.models import Basket
from mainapp.models import Product
from ordersapp.forms import OrderItemEditForm
from ordersapp.models import Order, OrderItem


class OrderList(ListView):
   model = Order

   def get_queryset(self):
       return Order.objects.filter(user=self.request.user, is_active=True)


   @method_decorator(login_required())
   def dispatch(self, *args, **kwargs):
       return super(ListView, self).dispatch(*args, **kwargs)


class OrderCreate(CreateView):
   model = Order
   success_url = reverse_lazy('order:list')
   fields = []

   def get_context_data(self, **kwargs):
       data = super(OrderCreate, self).get_context_data(**kwargs)
       OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemEditForm, extra=1)

       if self.request.POST:
           formset = OrderFormSet(self.request.POST)
       else:
           basket_items = Basket.get_items(self.request.user)
           if len(basket_items):
               OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemEditForm, extra=len(basket_items))
               formset = OrderFormSet()
               for num, form in enumerate(formset.forms):
                   form.initial['product'] = basket_items[num].product
                   form.initial['quantity'] = basket_items[num].quantity
                   form.initial['price'] = basket_items[num].product.price
               basket_items.delete()
           else:
               formset = OrderFormSet()

       data['orderitems'] = formset
       return data

   def form_valid(self, form):
       context = self.get_context_data()
       orderitems = context['orderitems']

       with transaction.atomic():
           form.instance.user = self.request.user
           self.object = form.save()
           if orderitems.is_valid():
               orderitems.instance = self.object
               orderitems.save()

       # удаляем пустой заказ
       if self.object.get_total_cost() == 0:
           self.object.delete()

       return super(OrderCreate, self).form_valid(form)

   @method_decorator(login_required())
   def dispatch(self, *args, **kwargs):
       return super(CreateView, self).dispatch(*args, **kwargs)




   #    def get_context_data(self, **kwargs):
   #     data = super().get_context_data(**kwargs)
   #     OrderFormSet = inlineformset_factory(Order,
   #                                          OrderItem,
   #                                          form=OrderItemEditForm,
   #                                          extra=1)
   #     if self.request.POST:
   #         formset = OrderFormSet(self.request.POST)
   #     else:
   #         formset = OrderFormSet()
   #
   #     data['orderitems'] = formset
   #     return data
   #
   #
   # def form_valid(self, form):
   #     context = self.get_context_data()
   #     orderitems = context['orderitems']
   #
   #     with transaction.atomic():
   #         form.instance.user = self.request.user
   #         self.object = form.save()
   #         if orderitems.is_valid():
   #             orderitems.instance = self.object
   #             orderitems.save()
   #
   #     if self.object.get_total_cost() == 0:
   #         self.object.delete()
   #
   #     return super().form_valid(form)


class OrderUpdate(UpdateView):
    model = Order
    success_url = reverse_lazy('order:list')
    fields = []

    def get_context_data(self, **kwargs):
        data = super(OrderUpdate, self).get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order,
                                             OrderItem,
                                             form=OrderItemEditForm,
                                             extra=1)
        if self.request.POST:
            data['orderitems'] = OrderFormSet(self.request.POST, instance=self.object)
        else:
            orderitems_formset = OrderFormSet(instance=self.object)
            for form in orderitems_formset.forms:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price
            data['orderitems'] = orderitems_formset
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()

        # удаляем пустой заказ
        if self.object.get_total_cost() == 0:
            self.object.delete()

        return super(OrderUpdate, self).form_valid(form)

    @method_decorator(login_required())
    def dispatch(self, *args, **kwargs):
        return super(UpdateView, self).dispatch(*args, **kwargs)

    # model = Order
    # success_url = reverse_lazy('order:list')
    # fields = []
    #
    # def get_context_data(self, **kwargs):
    #     data = super().get_context_data(**kwargs)
    #     OrderFormSet = inlineformset_factory(
    #         Order,
    #         OrderItem,
    #         form=OrderItemEditForm,
    #         extra=1
    #     )
    #     if self.request.POST:
    #         formset = OrderFormSet(self.request.POST, instance=self.object)
    #     else:
    #         formset = OrderFormSet(instance=self.object)
    #
    #
    #     data['orderitems'] = formset
    #     return data
    #
    # def form_valid(self, form):
    #     context = self.get_context_data()
    #     orderitems = context['orderitems']
    #
    #     with transaction.atomic():
    #         # form.instance.user = self.request.user
    #         self.object = form.save()
    #         if orderitems.is_valid():
    #             orderitems.instance = self.object
    #             orderitems.save()
    #
    #     if self.object.get_total_cost() == 0:
    #         self.object.delete()
    #
    #     return super().form_valid(form)


class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('order:list')


class OrderRead(DetailView):
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderRead, self).get_context_data(**kwargs)
        context['title'] = 'order details'
        return context

    @method_decorator(login_required())
    def dispatch(self, *args, **kwargs):
        return super(DetailView, self).dispatch(*args, **kwargs)


def forming_complete(request, pk):
   order = get_object_or_404(Order, pk=pk)
   order.status = Order.SENT_TO_PROCEED
   order.save()

def get_product_price(request, pk):
   if request.is_ajax():
       product = Product.objects.filter(pk=int(pk)).first()
       if product:
           return JsonResponse({'price': product.price})
       else:
           return JsonResponse({'price': 0})

# @receiver(pre_save, sender=Basket)
# @receiver(pre_save, sender=Order)
# def products_quantity_update_save(sender, undate_fields, instance, **kwargs):
#     if instance.pk:
#         instance.product.quantity -= instance.quantity - instance.get_item(instance.pk).quantity
#     else:
#         instance.product.quantity -= instance.quantity
#     instance.product.save()
#
#
# @receiver(pre_delete, sender=Basket)
# @receiver(pre_delete, sender=Order)
# def products_quantity_update_delete(sender, instance, **kwargs):
#     instance.product.quantity += instance.quantity
#     instance.product.save()