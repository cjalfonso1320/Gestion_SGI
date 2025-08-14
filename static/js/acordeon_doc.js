$(function () {
  // Primer nivel
  $(".doc-accordion .doc-section").click(function () {
    const content = $(this).next(".doc-content");
    $(".doc-accordion .doc-content").not(content).slideUp();
    $(".doc-accordion .doc-subcontent").slideUp();
    content.slideToggle();
  });

  // Segundo nivel
  $(".doc-accordion .doc-subsection").click(function () {
    const subcontent = $(this).next(".doc-subcontent");
    $(this).siblings(".doc-subcontent").not(subcontent).slideUp();
    subcontent.slideToggle();
  });

  // Tercer nivel
  $(".doc-accordion .doc-subsubsection").click(function () {
    const subsub = $(this).next(".doc-subsubcontent");

    // Cierra otros del mismo nivel
    $(this).siblings(".doc-subsubcontent").not(subsub).slideUp();
    subsub.slideToggle();
  });

    $(function () {
    // Primer nivel
    $(".sst-accordion .sst-section").click(function () {
      const content = $(this).next(".sst-content");
      $(".sst-accordion .sst-content").not(content).slideUp();
      $(".sst-accordion .sst-subcontent").slideUp();
      content.slideToggle();
    });

    // Segundo nivel
    $(".sst-accordion .sst-subsection").click(function () {
      const subcontent = $(this).next(".sst-subcontent");
      $(this).siblings(".sst-subcontent").not(subcontent).slideUp();
      subcontent.slideToggle();
    });
  });
});


