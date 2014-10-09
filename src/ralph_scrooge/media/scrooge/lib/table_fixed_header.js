/*
Fixed table header on scroll
*/

(function($) {
   $.fn.fixedHeader = function() {
      return this.each(function() {
         var $table = $(this),
             $headerFixed,
             lastScrollTop = 0,
             lastScrollLeft = 0;

         function init() {
            $headerFixed = $table.clone();
            $headerFixed.find("tbody").remove();
            $headerFixed.addClass("fixed");
            $headerFixed.insertBefore($table);
         }

         function resizeFixedHeader() {
            // set fixed header table width to properly display cell width
            $headerFixed.css("min-width", $table.outerWidth() + "px");
            // set width for each header cell
            $headerFixed.find("th").each(function(index) {
               $(this).css("min-width", $table.find("th").eq(index).outerWidth() + "px");
            });

            scrollHandler();
         }

         function scrollHandler() {
            var scrollTop = $(this).scrollTop(),
                scrollLeft = $(this).scrollLeft();

            if(scrollTop != lastScrollTop){
               lastScrollTop = scrollTop;
               var tableOffsetTop = $table.offset().top,
                   tableOffsetBottom = tableOffsetTop + $table.height() - $headerFixed.height();
               // hide or show header table
               if(scrollTop < tableOffsetTop || scrollTop > tableOffsetBottom){
                  if(!$headerFixed.is(':hidden')){
                     $headerFixed.hide();
                  }
               }
               else if($headerFixed.is(":hidden")){
                  $headerFixed.show();
               }
            }
            else if(scrollLeft != lastScrollLeft){
               lastScrollLeft = scrollLeft;
               var tableOffsetLeft = $table.offset().left;
               // apply header table position from left (if horizontal scroll)
               $headerFixed.css({
                 'left': -scrollLeft + tableOffsetLeft
               });
            }
         }

         $(window).resize(resizeFixedHeader);
         $(window).scroll(scrollHandler);

         init();
         resizeFixedHeader();
      });
   };
})(jQuery);

$(document).ready(function(){
   $("table.fixed-header").fixedHeader();
});
