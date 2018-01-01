var bn = bn || {};

;(function(namespace, undefined) {
  namespace.names = function(url) {
    var _names = []
    var _fuse = null;
    var _on = {};
    var _loaded = false;

    var _fuse_options = {
      caseSensitive: false,
      includeScore: false,
      shouldSort: true,
      threshold: 0.3,
      maxPatternLength: 32,
    };

    function _unique_in_array(value, index, self) { 
      return self.indexOf(value) === index;
    }

    var _typeahead = {};
   

		d3.json('data/namelist.json', function(error, data) {
      if (error) {
        console.warn(error);
        return;
      }
      _names = data.names;
			_fuse = new Fuse(_names, _fuse_options);
      _names.forEach(function(name) {
        for (var i = 1; i < name.length; i++) {
          var key = name.substring(0, i+1).toLowerCase();
          if (!_typeahead.hasOwnProperty(key)) {
            _typeahead[key] = [];
          }
          _typeahead[key].push(name);
        }
      });
      _loaded = true;
      if (_on.hasOwnProperty("load")) {
        _on["load"](_names);
      }
    });


    return {
      similar: function(seeds, limit) {
        limit = limit || 10;
        var candidates = [];
        seeds.forEach(function(name) {
          var locations = _fuse.search(name);
          if (locations.length > limit) {
            locations = locations.slice(0, limit);
          }
          candidates = candidates.concat(locations.map(function(index) { return _names[index];}));
        });

        /* remove duplicate candidates */
        candidates = candidates.filter(_unique_in_array);
        /* remove candidates in seeds */
        candidates = candidates.filter(function(value) { return seeds.indexOf(value) == -1; })

        /* shuffle in place*/
        for (var i = candidates.length-1; i >=0; i--) {
            var randomIndex = Math.floor(Math.random()*(i+1)); 
            var itemAtIndex = candidates[randomIndex]; 
            candidates[randomIndex] = candidates[i]; 
            candidates[i] = itemAtIndex;
        }


        /* return up to limit */
        return candidates.slice(0, limit);
      },

      all: _names,

      autocomplete: function(prefix) {
        var key = prefix.toLowerCase();
        return _typeahead[key] || [];
      },

      random: function() {
        return _names[Math.floor(Math.random() * _names.length)];
      },

      on: function() {
        if (arguments.length == 1) {
          return _on[arguments[0]];
        }
        else if (arguments.length > 1) {
          _on[arguments[0]] = arguments[1];
        }
        return this;
      }
    };
  }
})(bn);
