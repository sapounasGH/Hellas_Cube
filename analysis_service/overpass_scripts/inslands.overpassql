#islands
[out:json][timeout:120];
area["ISO3166-1"="GR"]->.greece;
(
  	relation["place"="island"]["name"](area.greece);
);
out body;
>;
out skel qt;