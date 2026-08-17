#protected areas parks
[out:json][timeout:180];
area["ISO3166-1"="GR"]->.greece;
(

  relation["boundary"="national_park"]["name"](area.greece);
  relation["boundary"="protected_area"]["name"](area.greece);
  way["boundary"="protected_area"]["name"](area.greece);
  
  relation["leisure"="nature_reserve"]["name"](area.greece);
  way["leisure"="nature_reserve"]["name"](area.greece);
);
out body;
>;
out skel qt;