$(document).ready(function () {
  $('select').select2();

  cascadingDropdown();

});


function cascadingDropdown() {
  var $locations = $('#id_locations.cascade');
  // required to handle the plugin correctly, do not comment this.
  var selectedLocations = $locations.val() || [];
  $locations.find('option').remove();
  $locations.select2();

  var options = {
    selectBoxes: [
      {
        selector: '#id_dimension.cascade',
        paramName: 'dimension'
      },
      {
        selector: '#id_locations.cascade',
        requires: ['#id_dimension.cascade'],
        source: function (request, response) {
          var url = Urls['dimension:location-list-ajax'](request.dimension);
          $.getJSON(url, {kind: 'direct'}, function (result) {
            var data = result.items;
            var locations = $.map(data, function (item) {
              return {
                label: item.name,
                value: item.id,
                selected: selectedLocations.indexOf(item.id.toString()) != -1
              };
            });
            response(locations);
            $locations.select2({
              placeholder: locations.length + ' locations found.'
            });
          });
        }
      }
    ]
  };

  $('.showcase-container').cascadingDropdown(options);
}