var bn = bn || {};

;(function (namespace, undefined) {
  namespace.dataview = function() {
		var _min_year = 1880;
		var _max_year = 2016;
		var _min_value = 0;
		var _max_value = 1;

    /* available metrics for viewing data */
    var _metrics = [
      { 
        field:"popularity", 
        display:"Popularity", 
        invert_y: false, 
        source_data: "popularity", 
        transform: function(d) { return d;}
      },
      { 
        field:"rank", 
        display:"Rank", 
        invert_y: true,
        source_data: "rank", 
        transform: function(d) { return d;}
      },
      { 
        field:"per_million", 
        display:"Per Million Births", 
        invert_y: false,
        source_data: "popularity", 
        transform: function(d) { return Math.round(d * 1000000);}
      }
    ];
    var _current_metric = _metrics[0];

    /* available genders */
    var _genders = {
      male: true,
      female: true,
      agender: true
    };

    /** NAMES **/
		function _capitalize(s) {
			return s.charAt(0).toUpperCase() + s.slice(1);
		}
    var _names = [];
    var _name_data = {};
    var _data = {};

    function _update_range() {
      /* get range */
      var extremes = [];

      /* get maximum value of all popularities */
      _data.forEach(function(gender_data) {
        /* only get extremes if gender enabled/disabled */
        if (_genders[gender_data.gender]) {
          extremes = extremes.concat(d3.extent(gender_data.metric, function(x) { return x.value; }));
        }
      });
      if (extremes.length > 0) {
        extremes = d3.extent(extremes);
        _min_value = extremes[0];
        _max_value = extremes[1];
      }
      else {
        _min_value = 0;
        _max_value = 1;
      }

      /* TODO: update years? */
      /* TODO: on range change? */
      _call_handler("update", _data.filter(function(d) { return _genders[d.gender]; }));
    }

    function _merge_names() {
      /* TODO: this also needs to be called on update metric */
      data = [];
      var merge_data = {};
      _names.forEach(function(name) {
        d3.entries(_name_data[name]).forEach(function(gender_entry) {
          var gender = gender_entry.key;
          var d = gender_entry.value;
          if (!merge_data.hasOwnProperty(gender)) {
            merge_data[gender] = { gender: gender, names: [d.name], metric: d[_current_metric.field] };
          }
          else {
            merge_data[gender].names.push(d.name);
            merge_data[gender].metric = merge_data[gender].metric.concat(d[_current_metric.field]);
          }
        });
      });


      /* merge multiple names metric data */
      d3.keys(merge_data).forEach(function(gender) {
        merge_data[gender].metric = merge_data[gender].metric.reduce(function(sum, val) {
          var found = false;

          for (var i = 0; i < sum.length; i++) {
            if (sum[i].year == val.year) {
              sum[i].value += val.value;
              found = true;
            }
          }
          if (!found) {
            sum.push(val);
          }
          return sum;
        }, []);
        merge_data[gender].metric.sort(function(a, b) { return a.year - b.year });
      });


      /* turn object with name keys into an array */
      _data = d3.values(merge_data);

      _update_range();
      /* TODO: callback here? */
    }

    function _update_names() {
      /* load names */
      _names.forEach(function(name) {
        /* don't load names if already loaded */
        if (_name_data.hasOwnProperty(name)) {
          var ready = _names.every(function(n) {
            return d3.keys(_genders).every(function(g) {
              return _name_data.hasOwnProperty(n) ? _name_data[n].hasOwnProperty(g) : false;
            });
          });
          if (ready) {
            _merge_names();
          }
        }
        _name_data[name] = {};
        
        /* get urls for names */
        var base_url = 'data/' + name[0].toLowerCase() + '/' + _capitalize(name); 
        var gender_urls = {
          agender: base_url + '_A.json',
          male: base_url + '_M.json',
          female: base_url + '_F.json'
        };

        /* load and format name data */
        d3.keys(_genders).forEach(function(gender) {
          d3.json(gender_urls[gender], function(error, name_data) {
            if (error) {
              console.warn(error);
            }

            var info = {
              gender: gender,
              name: name
            };
            _metrics.forEach(function(m) {
              info[m.field] = [];
            });

            if (!error) {
              /* load and transform metric data */
              _metrics.forEach(function(m) {
                if (name_data.hasOwnProperty(m.source_data)) {
                  var field_data = name_data[m.source_data];
                  for (var i = _min_year; i < _max_year; i++) {
                    if (field_data.hasOwnProperty(i)) {
                      info[m.field].push({
                        year: i,
                        value: m.transform(field_data[i])
                      });
                    }
                  }
                }
              });
            }

            /* store in global object and check if everything is loaded */
            _name_data[name][gender] = info;
            var ready = _names.every(function(n) {
              return d3.keys(_genders).every(function(g) {
                return _name_data.hasOwnProperty(n) ? _name_data[n].hasOwnProperty(g) : false;
              });
            });
            if (ready) {
              _merge_names();
            }
          });
        });
      });
    }


    var _handlers = {};
    function _call_handler(name, data) {
      if (_handlers.hasOwnProperty(name)) {
        _handlers[name](data);
      }
    }


    return {
      /* array of available metrics */
      metrics: function() {
        return _metrics;
      },

      /* get/set current metric */
      metric: function() {
        if (arguments.length == 0) {
          return _current_metric;
        }
        else {
          _current_metric = arguments[0];
          _merge_names();
        }
        return this;
      },

      /* get/set event handlers */
      on: function() {
        if (arguments.length == 1) {
          return _handlers[arguments[0]];
        }
        else if (arguments.length > 1) {
          if (arguments[1] == null) {
            delete _handlers[arguments[0]];
          }
          else {
            _handlers[arguments[0]] = arguments[1];
          }
        }
        return this;
      },

      /** RANGE **/
      minimum_year: function() { return _min_year; },
      maximum_year: function() { return _max_year; },
      extent_years: function() { return [_min_year, _max_year]; },
      minimum_value: function() { return _min_value; },
      maximum_value: function() { return _max_value; },
      extent_values: function() { return [_min_value, _max_value]; },

      /** GENDERS **/
      genders: function() {
        return d3.keys(_genders);
      },

      /* 1 argument returns whether a gender is enable/disabled 
         2 arguments sets whether gender enabled/disabled
      */
      gender: function() {
        if (arguments.length == 1) {
          return _genders[arguments[0]];
        }
        else if (arguments.length > 1) {
          _genders[arguments[0]] = arguments[1];
          _update_range();
        }
        return this;
      },

      /** NAMES **/
      names: function() {
        if (arguments.length == 0) {
          return _names.slice();
        }
        _names = arguments[0];
        _update_names();
      },

      /** DATA **/
      data: function() {
        return _data.filter(function(d) { 
          return _genders[d.gender]; 
        }); 
      }
    };
  }
})(bn);

