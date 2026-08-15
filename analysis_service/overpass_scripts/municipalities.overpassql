[out:json][timeout:120];
area["ISO3166-1"="GR"]->.greece;
(
  relation["boundary"="administrative"]["admin_level"="8"](area.greece);
  relation["boundary"="administrative"]["admin_level"="7"](area.greece);
);
out body;
>;
out skel qt;