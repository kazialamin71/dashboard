/*!
 * Simple Font Awesome Icon Picker (Optimized for Odoo)
 * Original: (c) 2016-17 Aumkar Thakur
 * Modified by ChatGPT for Odoo safety & performance
 * License: MIT
 */

(function (jQuery) {
    jQuery(document).ready(function () {
        // Prevent running in POS or any screen without iconpicker
        if (
            window.location.hash.indexOf('point_of_sale') !== -1 ||
            jQuery('input.iconpicker').length === 0
        ) {
            return;
        }

        // Append hidden icon picker UI
        jQuery('body').prepend(
            '<div class="howl-iconpicker-outer" style="display:none;">' +
                '<div class="howl-iconpicker-middle">' +
                    '<div class="howl-iconpicker">' +
                        '<div class="howl-closebtn"></div>' +
                        '<input type="text" class="srchicons" placeholder="Search icon e.g. google" />' +
                        '<div class="iconsholder"></div>' +
                    '</div>' +
                    '<div class="howl-iconpicker-close">Close</div>' +
                '</div>' +
            '</div>'
        );

        // Close picker when clicking outside or on close
        jQuery('.howl-iconpicker-close, .howl-iconpicker-outer').on('click', function () {
            jQuery('.howl-iconpicker-outer').hide();
        });
        jQuery('.howl-iconpicker').on('click', function (e) {
            e.stopPropagation();
        });

        // Search filter inside icon picker
        jQuery(document).on('keyup', '.howl-iconpicker .srchicons', function () {
            var filter = jQuery(this).val().toLowerCase();
            jQuery('.howl-iconpicker .geticonval').each(function () {
                var text = jQuery(this).text().toLowerCase();
                jQuery(this).toggle(text.indexOf(filter) > -1);
            });
        });
    });

    // Define icon picker plugin
    jQuery.fn.iconpicker = function (selector) {
        var fontawesomeicon =
            '500px address-book address-book-o address-card address-card-o adjust adn align-center align-justify align-left align-right amazon ambulance american-sign-language-interpreting anchor android angellist angle-double-down angle-double-left angle-double-right angle-double-up angle-down angle-left angle-right angle-up apple archive area-chart arrow-circle-down arrow-circle-left arrow-circle-o-down arrow-circle-o-left arrow-circle-o-right arrow-circle-o-up arrow-circle-right arrow-circle-up arrow-down arrow-left arrow-right arrow-up arrows arrows-alt arrows-h arrows-v assistive-listening-systems asterisk at audio-description backward balance-scale ban bandcamp bar-chart bar-chart-o barcode bars bath battery battery-empty battery-full battery-half battery-quarter bed beer behance behance-square bell bell-o bell-slash bicycle binoculars birthday-cake bitbucket bitbucket-square black-tie blind bluetooth bluetooth-b bold bolt bomb book bookmark bookmark-o briefcase bug building building-o bullhorn bullseye bus buysellads calculator calendar calendar-check-o calendar-minus-o calendar-o calendar-plus-o calendar-times-o camera camera-retro car caret-down caret-left caret-right caret-up cart-arrow-down cart-plus cc cc-amex cc-discover cc-mastercard cc-paypal cc-visa certificate check check-circle check-square chevron-down chevron-left chevron-right chevron-up child chrome circle circle-o clipboard clock-o clone close cloud cloud-download cloud-upload code code-fork codepen coffee cog cogs columns comment comment-o comments compass compress copy copyright credit-card crop crosshairs css3 cube cubes cutlery database deaf delicious desktop deviantart diamond digg dollar download dribbble dropbox drupal edit eject ellipsis-h ellipsis-v envelope envelope-o envelope-open envelope-open-o envelope-square eraser eur exchange exclamation exclamation-circle expand external-link external-link-square eye eye-slash facebook facebook-official facebook-square fast-backward fast-forward female fighter-jet file file-archive-o file-audio-o file-code-o file-excel-o file-image-o file-movie-o file-pdf-o file-powerpoint-o file-sound-o file-text file-text-o file-video-o file-word-o film filter fire flag flag-checkered flag-o flask flickr floppy-o folder folder-o folder-open folder-open-o font font-awesome forward foursquare free-code-camp gamepad gavel gear gears gift git git-square github github-alt github-square glass globe google google-plus google-plus-square graduation-cap gratipay group h-square hand-lizard-o hand-o-down hand-o-left hand-o-right hand-o-up hand-paper-o hand-peace-o hand-pointer-o hand-rock-o hand-scissors-o hand-spock-o handshake-o hashtag hdd-o headphones heart heart-o heartbeat history home hospital-o hourglass hourglass-end hourglass-half hourglass-o hourglass-start html5 i-cursor id-badge id-card id-card-o image inbox indent info info-circle inr instagram internet-explorer italic joomla key keyboard-o language laptop leaf lemon-o level-down level-up life-ring lightbulb-o line-chart link linkedin linkedin-square linux list list-alt list-ol list-ul location-arrow lock long-arrow-down long-arrow-left long-arrow-right long-arrow-up magic magnet mail-forward mail-reply mail-reply-all male map map-marker map-o map-pin map-signs mars mars-double mars-stroke mars-stroke-h mars-stroke-v medium medkit meh-o mercury microphone microphone-slash minus minus-circle minus-square mobile mobile-phone money moon-o motorcycle mouse-pointer music navicon newspaper-o object-group object-ungroup opencart openid opera outdent pagelines paint-brush paper-plane paper-plane-o paperclip paragraph paste pause pause-circle pause-circle-o paw paypal pencil pencil-square percent phone phone-square picture-o pie-chart pinterest pinterest-p pinterest-square plane play play-circle play-circle-o plug plus plus-circle plus-square podcast power-off print puzzle-piece qq qrcode question question-circle quote-left quote-right random recycle reddit reddit-square refresh registered remove reorder reply reply-all retweet road rocket rotate-left rotate-right rss rss-square ruble rupee safari save scissors search search-minus search-plus sellsy send server share share-alt share-square share-square-o shield ship shopping-bag shopping-basket shopping-cart sign-in sign-out signal sitemap skype slack sliders slideshare smile-o snapchat snapchat-ghost snapchat-square snowflake-o soccer-ball-o sort sort-alpha-asc sort-alpha-desc sort-amount-asc sort-amount-desc sort-asc sort-desc sort-down sort-numeric-asc sort-numeric-desc sort-up soundcloud space-shuttle spinner spotify square square-o stack-exchange stack-overflow star star-half star-half-o star-o steam step-backward step-forward stethoscope sticky-note stop stop-circle stop-circle-o street-view strikethrough stumbleupon stumbleupon-circle subscript subway suitcase sun-o sup script table tablet tachometer tag tags tasks taxi telegram television terminal text-height text-width th th-large th-list thumb-tack thumbs-down thumbs-o-down thumbs-o-up thumbs-up ticket times times-circle times-circle-o tint toggle-off toggle-on trademark train transgender trash trash-o tree trello tripadvisor trophy truck tumblr tumblr-square twitter twitter-square umbrella underline undo universal-access university unlink unlock upload usd user user-circle user-md user-plus user-secret user-times users venus venus-double venus-mars viacoin video-camera vimeo vimeo-square vine vk volume-down volume-off volume-up warning wechat weibo whatsapp wheelchair wifi wikipedia-w windows wordpress wrench xing xing-square yahoo yelp youtube youtube-play youtube-square',
            fontawesomeiconArray = fontawesomeicon.split(' ');

        var iconsLoaded = false;

        jQuery(this).focusin(function () {
            jQuery('.howl-iconpicker-outer').css('display', 'table');

            // Lazy-load icons only once
            if (!iconsLoaded) {
                var holder = jQuery('.howl-iconpicker .iconsholder');
                holder.empty();
                for (var i = 0; i < fontawesomeiconArray.length; i++) {
                    holder.append(
                        '<p class="geticonval"><i class="fa fa-' +
                            fontawesomeiconArray[i] +
                            '"></i> ' +
                            fontawesomeiconArray[i] +
                            '</p>'
                    );
                }
                iconsLoaded = true;
            }

            var whichInput = jQuery(this);
            jQuery('.howl-iconpicker .geticonval').off('click').on('click', function () {
                var iconName = jQuery(this).text().trim();
                jQuery('.howl-iconpicker .geticonval').removeClass('selectedicon');
                jQuery(this).addClass('selectedicon');
                whichInput.val('fa-' + iconName).change();
                jQuery('.howl-iconpicker-outer').hide();
            });
        });
    };
})(jQuery);
