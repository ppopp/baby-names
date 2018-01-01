var bn = bn || {};

;(function(namespace, undefined) {
  namespace.slider = function(svg) {

    
    var _domain = [0, 1];
    var _margin = {after: 50, before: 50};
    var _width = +svg.attr("width") - _margin.before - _margin.after;
    var _height = +svg.attr("height");
    var _upper_value = _domain[0];
    var _lower_value = _domain[1];
    var _is_horizontal = true;
    var _handle_loc_attr = "cx";
    var _track_range_pos1_attr = "x1";
    var _track_range_pos2_attr = "x2";

    /*
    var _scale = d3.scaleLinear()
        .domain(_domain)
        .range([0, _width])
        .clamp(true);
    */
    var _scale = d3.scaleLinear()
        .domain(_domain)
        .clamp(true);

    function orient(is_horizontal) {
      if (_is_horizontal == is_horizontal) {
        return;
      }
      _is_horizontal = is_horizontal;

      if (_is_horizontal) {
        _handle_loc_attr = "cx";
        _track_range_pos1_attr = "x1";
        _track_range_pos2_attr = "x2";
        _slider.attr("transform", "translate(" + _margin.before + "," + _height / 2 + ")");
        _scale.range([0, _width]);
      }
      else {
        _handle_loc_attr = "cy";
        _track_range_pos1_attr = "y1";
        _track_range_pos2_attr = "y2";
        _slider.attr("transform", "translate(" + _width / 2  + "," + _margin.before + ")");
        /* TOOD: flip? */
        _scale.range([0, _height]);
      }
    }
    /*
    var _slider = svg.append("g")
        .attr("class", "slider")
        .attr("transform", "translate(" + _margin.before + "," + _height / 2 + ")");
    */
    var _slider = svg.append("g")
        .attr("class", "slider");

    function set_values(lower_value, upper_value) {
      _upper_value = upper_value;
      _upper_handle.attr(_handle_loc_attr, _scale(_upper_value));
      _lower_value = lower_value;
      _lower_handle.attr(_handle_loc_attr, _scale(_lower_value));
      _slider.select(".bn-slider-track-range")
        .attr(_track_range_pos1_attr, _scale(_lower_value))
        .attr(_track_range_pos2_attr, _scale(_upper_value));
    }

    function update_ticks() {
      var ticks = _slider.select(".bn-slider-ticks")
        .selectAll("text")
        .data(_scale.ticks(10));
      ticks.exit().remove();
      ticks.enter().append("text") 
        .attr("text-anchor", "middle")
        .merge(ticks)
        .attr("x", _scale)
        .text(function(d) { console.log(d); return d; });
    }
    _slider.append("line")
        .attr("class", "bn-slider-track")
        .attr(_track_range_pos1_attr, _scale.range()[0])
        .attr(_track_range_pos2_attr, _scale.range()[1])
      .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "bn-slider-track-inset")
      .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "bn-slider-track-range")
      .select(function() { return this.parentNode.appendChild(this.cloneNode(true)); })
        .attr("class", "bn-slider-track-overlay")
        .call(d3.drag()
            .on("start.interrupt", function() { _slider.interrupt(); })
            .on("start drag", function() { 
              var value = _scale.invert(d3.event.x);
              /* find nearest handle */
              if (Math.abs(value - _upper_value) < Math.abs(value - _lower_value)) {
                set_values(_lower_value, value);
              }
              else {
                set_values(value, _upper_value);
              }
              if (_on.hasOwnProperty("drag")) {
                _on["drag"]([_lower_value, _upper_value]);
              }
            }));

    /* TODO: finish orienting things */

    _slider.insert("g", ".bn-slider-track-overlay")
        .attr("class", "bn-slider-ticks")
        .attr("transform", "translate(0," + 18 + ")")
      .selectAll("text")
      .data(_scale.ticks(10))
      .enter().append("text")
        .attr("x", _scale)
        .attr("text-anchor", "middle")
        .text(function(d) { return d; });

    var _upper_handle = _slider.insert("circle", ".bn-slider-track-overlay")
        .attr("class", "bn-slider-upper-handle")
        .attr("r", 9)
        .attr("cx", _scale(_upper_value));
    var _lower_handle = _slider.insert("circle", ".bn-slider-track-overlay")
        .attr("class", "bn-slider-lower-handle")
        .attr("r", 9)
        .attr("cx", _scale(_lower_value));


    var _on = {};    
    
    return {
      on: function() {
        if (arguments.length == 1) {
          return _on[arguments[0]];
        }
        else if (arguments.length > 1) {
          _on[arguments[0]] = arguments[1];
        }
        return this;
      },
      domain: function() {
        if (arguments.length == 0) {
          return _domain;
        }
        _domain = arguments[0]
        _scale.domain(_domain);
        set_values(_domain[0], _domain[1]);
        update_ticks();

        return this;
      },
      values: function() {
        if (arguments.length == 0) {
          return [_lower_value, _upper_value];
        }
        else if (arguments.length == 1) {
          set_values(arguments[0][0], arguments[0][1]);
        }
        else if (arguments.length > 1) {
          set_values(arguments[0], arguments[1]);
        }
        return this;
      }

    };
  }
})(bn);
