(function () {
    var jquery_version = '3.3.1';
    var site_url = 'http://localhost:8000';
    var static_url = site_url + '/static/';
    var min_width = 100;
    var min_height = 100;

    function bookmarklet(msg) {
        //here goes our bookmark code
        //load css
        var css = jQuery('<link>');
        css.attr(
            {
                rel: 'stylesheet',
                type: 'text/css',
                href: static_url + 'css/bookmarklet.css?r=' + Math.floor(Math.random() * 99999999999999999999)
            });
        jQuery('head').append(css);

        box_html = '<div id="bookmarklet"><a href="#" id="close">&times;</a><h1>Select an Image to bookmark:</h1><div class="images border border-4"></div></div>';
        jQuery('body').append(box_html);
        //close event
        jQuery('#bookmarklet #close').click(function () {
            jQuery('#bookmarklet').remove();
        });
    };
//find images and display item
    jQuery.each(jQuery('img[src$="jpg"]'), function (index, image) {

        if (jQuery(image).width() >= min_width && jQuery(image).height() >= min_height) {
            image_url = jQuery(image).attr('src');
            jQuery('#bookmarklet .images').append('<a href="#"><img src="' + image_url + '" alt="Image is not " class="w-25"></a>')

        }
    });
    //	when	an	image	is	selected	open	URL	with	it
    jQuery('#bookmarklet .images a').click(function (e) {

        selected_image = jQuery(this).children('img').attr('src');
        alert(selected_image)
        //	hide	bookmarklet
        jQuery('#bookmarklet').hide();
        //	open	new	window	to	submit	the	image
        window.open(site_url + '/images/create/?title=' + encodeURIComponent(jQuery('title').text()) + '&url=' + encodeURIComponent(selected_image), '_blank');
    });


    //check jquery is loaded
    if (typeof window.jQuery != 'undefined') {
        bookmarklet();

    } else {

        //check the conflicts
        var conflict = typeof window.$ != 'undefined';
        //create the script and point to Google Api
        var script = document.createElement('script');
        script.src = '//ajax.googleapis.com/ajax/libs/jquery/' + jquery_version + '/jquery.min.js'
        //add the javascript to the head for processing
        document.head.appendChild(script);
        //create a way to wait until scipt loading
        var attempts = 50;
        (function () {
            //check afain if jquery is undegined
            if (typeof window.jQuery == 'undefined') {
                if (--attempts > 0) {
                    window.setTimeout(arguments.callee, 250)
                } else {
                    alert('An error occured while loading jquery')
                }

            } else {
                bookmarklet();
            }
        })();
    }


})();
