window.onload = function () {
    var _quantity, _price, orderitem_num, delta_quantity, orderitem_quantity, delta_cost;

    var quantity_arr = [];
    var price_arr = [];
    var total_forms = parseInt($('input[name=orderitems-TOTAL_FORMS]').val());
    var order_total_quantity = parseInt($('.order_total_quantity').text()) || 0;
    var order_total_price = parseFloat($('.order_total_cost').text()) || 0;

    for(var i=0, i < total_forms, i++){
        _quantity = parseInt($('input[name=orderitems-' + i + '-quantity]').val());
        _price = parseFloat($('.orderitems-' + i + '-price').text().replace(',', '.'));

        quantity_arr[i] = _quantity;
        if(_price) {
            price_arr[i] = _price;
        } else {
            price_arr[i] = 0;
        }
    }

    $('.order_form').on('click', 'input[type=number]', function(){
        var target = event.target
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-quantity'));
        if(price_arr[orderitem_num]){
            orderitem_quantity = parseInt(target.value);
            delta_quantity = orderitem_quantity - quantity_arr[orderitem_num];
            quantity_arr[orderitem_num] = orderitem_quantity;
            orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
        }
    });

    $('.order_form').on('click', 'input[type=checkbox]', function(){
        var target = event.target
        orderitem_num = parseInt(target.name.replace('orderitems-', '').replace('-DELETE'));
        if (target.checked) {
            delta_quantity = -quantity_arr[orderitem_num];
        }
        else {
            delta_quantity = quantity_arr[orderitem_num];
        }
        orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
    });


    function orderSummaryUpdate(orderitem_price, delta_quantity){
        delta_cost = orderitem_price * delta_quantity;
        order_total_price = Number((order_total_price + delta_cost).toFixed(2));
        order_total_quantity = orderitem_quantity + delta_quantity;

        $('.order_total_quantity').text(order_total_quantity.toString());
        $('.order_total_cost').text(order_total_price.toString());
    }
    $('.formset_row').formset({
        addText: 'Добавить продукт',
        deleteText: 'Удалить',
        prefix: 'orderitems',
        removed: deleteOrderItem(),
    });

    function deleteOrderItem(row) {
        var target_name = row[0].querySelector('input(type=number)').name;
        orderitem_num = parseInt(target_name.replace('orderitems-', '').replace('-quantity'));

        delta_quantity = -quantity_arr[orderitem_num];
        orderSummaryUpdate(price_arr[orderitem_num], delta_quantity);
    }
}

    /*
    // можем получить DOM-объект меню через JS
    var menu = document.getElementsByClassName('menu')[0];
    menu.addEventListener('click', function () {
        console.log(event);
        event.preventDefault();
    });
    
    // можем получить DOM-объект меню через jQuery
    $('.menu').on('click', 'a', function () {
        console.log('event', event);
        console.log('this', this);
        console.log('event.target', event.target);
        event.preventDefault();
    });
   
    // получаем атрибут href
    $('.menu').on('click', 'a', function () {
        var target_href = event.target.href;
        if (target_href) {
            console.log('нужно перейти: ', target_href);
        }
        event.preventDefault();
    });
    */
    
    // добавляем ajax-обработчик для обновления количества товара
//    $('.basket_list').on('click', 'input[type="number"]', function () {
//        var target_href = event.target;
//
//        if (target_href) {
//            $.ajax({
//                url: "/basket/edit/" + target_href.name + "/" + target_href.value + "/",
//
//                success: function (data) {
//                    $('.basket_list').html(data.result);
//                    console.log('ajax done');
//                },
//            });
//
//        }
//        event.preventDefault();
//    });
//
//}