$(document).ready(function(){
  var currPage = ".page1";
  $('.page2').hide();
  $('.page3').hide();

  $(function () {
      $('.toggle1').on("click", function (e) {
          console.log("cl");
          e.preventDefault();
          if(currPage!=".page1"){
            $(currPage).hide("slide", {direction: "right"}, "fast");
            $('.page1').delay(100).fadeIn();
            currPage = ".page1";
            $('.active').removeClass('active');
            $('.li1').addClass('active');
          }
      });
      $('.toggle2').on("click", function (e) {
        console.log("cl");
        e.preventDefault();
        if(currPage!=".page2"){
          $(currPage).hide("slide", {direction: "right"}, "fast");
          $('.page2').delay(100).fadeIn();
          currPage = ".page2";
          $('.active').removeClass('active');
          $('.li2').addClass('active');
        }
      });
      $('.toggle3').on("click", function (e) {
        console.log("cl");
          e.preventDefault();
          if(currPage!=".page3"){
            $(currPage).hide("slide", {direction: "right"}, "fast");
            $('.page3').delay(100).fadeIn();
            currPage = ".page3";
            $('.active').removeClass('active');
            $('.li3').addClass('active');
          }
      });
  });

  var currScatter;
  $(function () {
    $('#scatter').on("click", function (e) {
      if(currScatter){
        $(currScatter).remove('.highlight');
      }
      console.log("hi");
      console.log(this);
      $(this).addClass('.highlight');
    });
  });

});