from resource_engine import recommend_resources

result = recommend_resources(

    event_type="unplanned",

    corridor="Mysore Road",

    junction="SadahalliGateJunc(AirportRd)",

    tii=88

)

print(result)