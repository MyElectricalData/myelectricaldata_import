/*!
 * jQuery FAB Button v1.1.0 (https://github.com/smachs/jquery-fab-button)
 * Copyright 2014-2019 Materialize & Smachs
 * MIT License (https://raw.githubusercontent.com/Dogfalo/materialize/master/LICENSE)
 */
/*!
 * jQuery FAB Button v1.1.0 (https://github.com/smachs/jquery-fab-button)
 * Copyright 2014-2019 Materialize & Smachs
 * MIT License (https://raw.githubusercontent.com/Dogfalo/materialize/master/LICENSE)
 */
/*!
 * jQuery FAB Button v1.1.0 (https://github.com/smachs/jquery-fab-button)
 * Copyright 2014-2019 Materialize & Smachs
 * MIT License (https://raw.githubusercontent.com/Dogfalo/materialize/master/LICENSE)
 */
$(document).ready(function () {
    // jQuery reverse
    $.fn.reverse = [].reverse;

    // Hover behaviour: make sure this doesn't work on .click-to-toggle FABs!
    $(document).on('mouseenter.fixedActionBtn', '.fixed-action-btn:not(.click-to-toggle)', function (e) {
    		// Open
        var $this = $(this);
        openFABMenu($this);
        
        // Change background based in data attributes
        $("#first-fab").css('background', function () {
        	return $(this).data('fabcolor')
        });
        $("#second-fab").css('background', function () {
        	return $(this).data('fabcolor')
        });
        $("#third-fab").css('background', function () {
        	return $(this).data('fabcolor')
        });
        $("#fourth-fab").css('background', function () {
        	return $(this).data('fabcolor')
        });
    });
    $(document).on('mouseleave.fixedActionBtn', '.fixed-action-btn:not(.click-to-toggle)', function (e) {
        var $this = $(this);
        closeFABMenu($this);
    });

    // Toggle-on-click behaviour.
    $(document).on('click.fixedActionBtn', '.fixed-action-btn.click-to-toggle > a', function (e) {
        var $this = $(this);
        var $menu = $this.parent();
        if ($menu.hasClass('active')) {
            closeFABMenu($menu);
        } else {
            openFABMenu($menu);
        }
    });
});

$.fn.extend({
    openFAB: function () {
        openFABMenu($(this));
    },
    closeFAB: function () {
        closeFABMenu($(this));
    }
});

var head= document.getElementsByTagName('head')[0];
var script= document.createElement('script');
script.type= 'text/javascript';
script.src= '//cdnjs.cloudflare.com/ajax/libs/velocity/1.2.3/velocity.min.js';
head.appendChild(script);

var openFABMenu = function (btn) {
    $this = btn;
    if ($this.hasClass('active') === false) {

        // Get direction option
        var horizontal = $this.hasClass('horizontal');
        var offsetY, offsetX;

        if (horizontal === true) {
            offsetX = 40;
        } else {
            offsetY = 40;
        }

        $this.addClass('active');
        $this.find('ul .btn-floating').velocity(
            { scaleY: ".4", scaleX: ".4", translateY: offsetY + 'px', translateX: offsetX + 'px' },
            { duration: 0 });

        var time = 0;
        $this.find('ul .btn-floating').reverse().each(function () {
            $(this).velocity(
                { opacity: "1", scaleX: "1", scaleY: "1", translateY: "0", translateX: '0' },
                { duration: 80, delay: time });
            time += 40;
        });
    }
};

var closeFABMenu = function (btn) {
    $this = btn;
    // Get direction option
    var horizontal = $this.hasClass('horizontal');
    var offsetY, offsetX;

    if (horizontal === true) {
        offsetX = 40;
    } else {
        offsetY = 40;
    }

    $this.removeClass('active');
    var time = 0;
    $this.find('ul .btn-floating').velocity("stop", true);
    $this.find('ul .btn-floating').velocity(
        { opacity: "0", scaleX: ".4", scaleY: ".4", translateY: offsetY + 'px', translateX: offsetX + 'px' },
        { duration: 80 }
    );
};
