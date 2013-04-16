var application = {
    formValidate: 
    {
        init: function()
        {
            $.extend($.validator.messages, {
                required: "Вы не заполнили поле",
                email: "Указанный E-mail некорректен",
                number: "Некорректный телефонный номер",
                minlength: "Не менее {0} символов",
                equalTo: "Пароли различаются",
            });
            $.extend($.validator.defaults, {
                errorClass: "error",
                errorElement: "span"
            });
            var self = this;
            $('form').each(function(){
                var form = $(this);
                var validator = form.validate({
                    invalidHandler: function(e, validator) {
                        // if (validator.numberOfInvalids()) 
                        //     alert('Вы заполнили форму не полностью');
                    },
                    onkeyup: false,
                    errorPlacement: function(label, element){
                        if(element.attr('name') != 'captcha')
                            label.addClass('error-description').insertAfter(element);

                        if(element.hasClass('small-error'))
                            label.addClass('small-error').insertAfter(element);

                        if(element.attr('type') == 'checkbox')
                            label.addClass('checkbox-error').insertAfter(element);
                    },
                });

                jQuery.validator.addClassRules({
                    req_verify: {
                        required: true,
                    },
                    pass_verify: {
                        required: true,
                        minlength: 6
                    },
                    pass_again_verify: {
                        equalTo: "#password",
                        required: true,
                        minlength: 6
                    }
                });

                if (form.hasClass('ajax-form')){
                    if (form.attr('enctype') == 'multipart/form-data')
                        self.iframeForm(form, validator);
                    else
                        self.ajaxForm(form, validator);
                }
            });
        },
        ajaxForm: function(form, validator)
        {
            var self = this;
            
            form.ajaxForm({
                dataType: 'json', 
                success: function(data)
                {
                    if (data['success']=='false'){
                        self.showErrors(data, validator);
                        return;
                    }
                    if (data['success']=='true'){
                        // form.slideUp(300);
                        // var message = form.next();
                        // message.find('p').text(data['results']['OK_MESSAGE']);
                        // message.slideDown(300);

                        if(data['results']['reboot_now'])
                        {
                            if(data['results']['url'])
                                window.location.replace(data['results']['url']);
                            else
                                window.location.reload();
                        }
                        else if(data['profile'] == true)
                        {
                            if(data['results']['has-changes'] == true)
                            {
                                var thanks = $('#thanks');
                                if(data['results']['OK_MESSAGE'])
                                    thanks.find('h2').html(data['results']['OK_MESSAGE']);  

                                $('.thanks-link').trigger('click');   
                            }
                        }
                        else
                        {
                            var thanks = $('#thanks');
                            if(data['results']['OK_MESSAGE'])
                                thanks.find('h2').html(data['results']['OK_MESSAGE']);  

                            // if(data['results']['reboot_now'])
                            //     window.location.reload();

                            if(data['results']['reboot'])
                                  thanks.find('a').bind("click", function(e){
                                      window.location.reload();
                                    });

                            $('.thanks-link').trigger('click');                     

                            var message = form.next();
                            form.hide();
                            message.show();
                        }
                    }
                }
            }); 
        },
        iframeForm: function(form, validator)
        {
            var self = this;
            form.submit(function(){
                var targetFrame = frame_name = 'frame' + new Date().getTime().toString();
                $('body').append('<iframe id="'+targetFrame+'" name="'+targetFrame+'" style="display:none;"></iframe>');
                
                var frame = $('#'+targetFrame);
                form.attr({target: targetFrame});
                frame.load(function()
                {
                    var data = frame.contents().find('body').text();
                    frame.remove();
                    data = $.parseJSON(data);
                    if (data['success']=='false'){
                        // form.get(0).reset();
                        self.showErrors(data, validator);
                        return;
                    }
                    if (data['success']=='true'){
                        form.slideUp(300);
                        var message = form.parent().append($('#'+form.attr('rel')));
                        message.slideDown(300);
                    }
                });
            });
        },
        showErrors: function(data, validator)
        {
            var obj = {};
            validator.showErrors(data['results']['ERROR_MESSAGE']);
            validator.showErrors(data['results']['ERRORS']);
        }
    },
    catalog: 
    {
        init: function()
        {
            $('#catalog-search a.reset').click(function() {
                var form = $('form').has(this);
                form.find('input[type="text"]').val('');
                form.submit();
                return false;
            });
            $('.view a.short').click(function() {
                $('.catalog-item ul').addClass('hidden');
                $('.view a').removeClass('active');
                $(this).addClass('active');
                return false;
            });
            $('.view a.detail').click(function() {
                // еслли на главной, то надо передти на страницу каталога
                if($(this).attr('href'))
                    return true;

                $('.catalog-item ul').removeClass('hidden');
                $('.view a').removeClass('active');
                $(this).addClass('active');
                return false;
            });
        },
    },
    basket: 
    {
        init: function()
        {
            var self = this;
            
            self.info(self.updateFloatBasket, self.getAjaxUrl());

            // добавить в корзину
            $(".catalog-item a.add").click(function () {
                var id = $(this).attr('rel'),
                    quantity = $(this).parent().find('input').val();

                self.add(id, quantity, self.updateFloatBasket, this);
                return false;
            });
            $('.buy .add').click(function () {
                var id = $(this).attr('rel'),
                    quantity = $(this).parent().find('input').val();

                self.add(id, quantity, self.updateFloatBasket, this);
                return false;
            });

            // увеличить количество на 1
            $('#basket .change-summ .plus').click(function () {
                var id = $(this).attr('rel'),
                    quantity = 1;

                self.add(id, quantity, self.updateBasket, this);
                return false;
            });

            // уменьшить количество на 1
            $('#basket .change-summ .minus').click(function () {
                var id = $(this).attr('rel'),
                    quantity = 1;

                if($(this).parent().find('input.change-val').val() <= 0)
                    return false;

                self.reduce(id, quantity, self.updateBasket, this);
                return false;
            });

            // деактивировать или активировать элемент корзины
            $('#basket .checker').click(function () {
                var id = $(this).find('span').attr('rel'),
                    url = $('#basket').attr('rel');

                if($(this).find('span').hasClass('checked'))
                    self.deactivate(id, self.updateBasket, false, url);
                else
                    self.activate(id, self.updateBasket, false, url);
            });

            // деактивировать элемент корзины
            $('#basket .delete').click(function () {
                var id = $(this).attr('rel'),
                    url = $('#basket').attr('rel');

                self.deactivate(id, self.updateBasket, false, url);
            });

            // выбор ФИЗ или ЮР лицо в корзине
            $('#basket .fiz-block .radio').click(function () {
                var url = $('#basket').attr('rel');

                var user_type =$(this).has('span.checked').next().text();

                if(user_type == 'Физическое лицо')
                    self.setUserType(url, 'fiz', function(){window.location.reload();});
                else if(user_type == 'Юридическое лицо')
                    self.setUserType(url, 'ur', function(){window.location.reload();});
            });

            // сохранить смету
            $('.bask-but.estimate').click(function () {
                var url = $('#basket').attr('rel');

                self.estimate(url, self.showEstimateDone, this);

                return false;
            });

        },
        getAjaxUrl: function()
        {
            var url = $('.basket-ajax-link').attr('href');

            return url;
        },
        updateFloatBasket: function(data)
        {
            var basket = $('#float-basket');
            
            if(data['totalQuantity'] > 0)
                basket.stop().animate({right:-27},{duration:400, easing:'easeOutSine'});

            basket.find('.sum').text(data['totalQuantity']);
            basket.find('.info-row .value').first().text(data['totalQuantity']);
            basket.find('.info-row .value').last().text(data['totalPrices']['actual'] + ' руб.');
        },
        updateBasket: function(data, sender)
        {
            $('.order-right .val').first().text(data['totalQuantity']);
            $('.order-right .val').last().text(data['totalPrices']['actual'] + ' р.');

            $('.basket-bottom-left .val').first().text(data['totalQuantity']);
            $('.basket-bottom-left .val').last().text(data['totalPrices']['actual'] + ' р.');

            $('.stock-val').text(data['totalDiscount'] + ' р.');

            $('.basket-row').has(sender).find('.col-6 .simple-price span').text(data['prices']['actual'] + ' р.');
            $('.basket-row').has(sender).find('.col-6 span.gold-price').text(data['prices']['gold'] + ' р.');
            $('.basket-row').has(sender).find('.col-6 span.silver-price').text(data['prices']['silver'] + ' р.');
        },
        showEstimateDone: function(data, sender)
        {
            var thanks = $('#thanks'),
                cabunet_url = $(sender).attr('rel');
            thanks.find('h2').html('Смета успешно создана!<br /> Вы можете сделать заказ по этой смете найдя ее в разделе <a href="' + cabunet_url + '">“Мои сметы"</a>');  

            $('.thanks-link').trigger('click')                   
        },
        add: function(id, quantity, callback, sender)
        {
            var url = $(sender).attr('href');

            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'add', product_id: id, quantity: quantity},
                dataType: 'json',
                success: function(data) {
                    if(data['error'])
                    {
                        var thanks = $('#thanks');
                        thanks.find('h2').html(data['error']);  

                        $('.thanks-link').trigger('click');
                    }
                    else
                        callback(data, sender);
                },
                fail: function(data) {
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
        reduce: function(id, quantity, callback, sender)
        {
            var url = $(sender).attr('href');

            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'reduce', product_id: id, quantity: quantity},
                dataType: 'json',
                success: function(data) {
                    callback(data, sender);
                },
                fail: function(data) {
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
        info: function(callback, url)
        {
            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'info'},
                dataType: 'json',
                success: function(data) {
                    callback(data);
                },
                fail: function(data) { 
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
        activate: function(id, callback, sender, url)
        {
            if(!url)
                var url = $(sender).attr('href');

            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'activate', product_id: id},
                dataType: 'json',
                success: function(data) {
                    if(callback)
                        callback(data, sender);
                },
                fail: function(data) {
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
        deactivate: function(id, callback, sender, url)
        {
            if(!url)
                var url = $(sender).attr('href');

            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'deactivate', product_id: id},
                dataType: 'json',
                success: function(data) {
                    if(callback)
                        callback(data, sender);
                },
                fail: function(data) {
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
        setUserType: function(url, userType, callback, sender)
        {
            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'set-usertype', user_type: userType},
                dataType: 'json',
                success: function(data) {
                    callback(data, sender);
                },
                fail: function(data) {
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
        estimate: function(url, callback, sender)
        {
            $.ajax({
                type: 'POST',
                url: url,
                data: {action: 'estimate'},
                dataType: 'json',
                success: function(data) {
                    callback(data, sender);
                },
                fail: function(data) {
                    // alert('Ошибка. Попробуйте снова.');
                }
            });
        },
    },
    order: 
    {
        init: function()
        {
            var self = this;
            
            $('input.liffting').change(function() {
                if(this.checked)
                {
                    $('.floor-input').addClass('req_verify');

                    var label = $('.floor-input').prev();
                    label.html( label.html() + ' <span class="req">*</span>' );
                }
                else
                {
                    $('.floor-input').removeClass('req_verify').removeClass('error');
                    $('.floor-input').next().remove();

                    var label = $('.floor-input').prev();
                    var labelHtml = label.html().replace(' <span class="req">*</span>','');
                    label.html( labelHtml );
                }
            });
            

            $('a.next-step').click(function () {
                $('form[name=order_form]').submit();

                return false;
            });

            // на странице доставки
            $('.express-open input:radio:checked').parents('.express-open').addClass('active');
        }
    },
    cabinet: 
    {
        init: function()
        {
            var self = this;
            
            $('.profile .save').click(function() {
                $('form').has(this).submit();
            });

            $('.close-cabinet a, a.logout').click(function () {
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('href'),
                    data: {action: 'logout'},
                    dataType: 'json',
                    success: function(data) {
                        window.location.reload();
                    },
                    fail: function(data) {
                        // alert('Ошибка. Попробуйте снова.');
                    }
                });

                return false;
            });

            $('.delete-profile a').click(function () {
                $.ajax({
                    type: 'POST',
                    url: $(this).attr('href'),
                    data: {action: 'deleteprofile'},
                    dataType: 'json',
                    success: function(data) {
                        var thanks = $('#thanks');
                        if(data['results']['OK_MESSAGE'])
                            thanks.find('h2').html(data['results']['OK_MESSAGE']);  

                        $('.thanks-link').trigger('click');
                    },
                    fail: function(data) {
                        // alert('Ошибка. Попробуйте снова.');
                    }
                });

                return false;
            }); 

            $('.total-button a').click(function () {
                var form = $('form').has($(this));
                
                form.find('input[name="action"]').val($(this).attr('rel'));
                form.submit();

                return false;
            });

            $('a.estimate-action').click(function () {
                var form = $('form').has($(this));
                
                form.find('input[name="action"]').val($(this).attr('rel'));
                form.submit();

                return false;
            });
        }
    }
}
$(document).ready(function(){
    (function() {
        this.formValidate.init();
        this.catalog.init();
        this.basket.init();
        this.order.init();
        this.cabinet.init();
    }).call(application);
});