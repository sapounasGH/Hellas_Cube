#national parks
[out:json][timeout:120];
area["ISO3166-1"="GR"]->.greece;
(
  	relation["boundary"="national_park"]["name"](area.greece);
);
out body;
>;
out skel qt;