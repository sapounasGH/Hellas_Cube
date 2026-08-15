#lakes and rivers
[out:json][timeout:120];
area["ISO3166-1"="GR"]->.greece;
(
	way["natural"="water"]["name"](area.greece);
  	relation["natural"="water"]["name"](area.greece);
);
out body;
>;
out skel qt;