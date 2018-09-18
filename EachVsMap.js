// The each method is meant to be an immutable iterator, where as the map method can be used as an iterator, but is really meant to manipulate the supplied array and return a new array.
// Another important thing to note is that the each function returns the original array while the map function returns a new array. If you overuse the return value of the map function you can potentially waste a lot of memory.
// For example:

var items = [1,2,3,4];

$.each(items, function() {
  alert('this is ' + this);
});

var newItems = $.map(items, function(i) {
  return i + 1;
});

// newItems is [2,3,4,5]
// You can also use the map function to remove an item from an array. For example:

var items = [0,1,2,3,4,5,6,7,8,9];

var itemsLessThanEqualFive = $.map(items, function(i) {
  // removes all items > 5
  if (i > 5) 
    return null;
  return i;
});
// itemsLessThanEqualFive = [0,1,2,3,4,5]