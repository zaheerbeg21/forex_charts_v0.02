var $selectSeries = $('#seriesID'),
  $selectEpisode = $('#episodeID'),
  $episodeOptions = $selectEpisode.find('option'),
  $tbody = $('#results tbody'),
  $rows = $tbody.find('tr');

function onSeriesChange() {
  var selectedSeries = $selectSeries.val() || '',
    $filteredOptions = $episodeOptions.prop('selected', false).detach();

  $filteredOptions = $filteredOptions.filter('[data-series="' + selectedSeries + '"]');
  $selectEpisode.append($filteredOptions).prop('disabled', $filteredOptions.length == 0);

  if ($filteredOptions.length) {
    $filteredOptions.first().prop('selected', true);
  } else {
    $selectEpisode.append($episodeOptions.filter('.placeholder')).prop('disabled', true);
  }

  filterTable();
}

function onEpisodeChange() {
  filterTable();
}

function filterTable() {
  var $filteredRows = $rows.detach(),
    selectedSeries = $selectSeries.val() || '',
    selectedEpisode = $selectEpisode.val() || '';

  if (selectedSeries != '') {
    $filteredRows = $filteredRows.filter('[data-series="' + selectedSeries + '"]');
    $filteredRows = $filteredRows.filter('[data-episode="' + selectedEpisode + '"]');
  }

  $tbody.append($filteredRows);
}

filterTable();
$selectSeries.on('change', onSeriesChange);
$selectEpisode.on('change', onEpisodeChange);