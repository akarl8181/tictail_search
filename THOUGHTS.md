
Should be possible to load all the data into memory.

Performance seems good so far.

Might need to filter out data not needed, like quantity and title.

Perhaps I can lazy load the products at the cost of speed vs memory.
Right now the memory footprint is 57mb

The slowest part seems to be `jsonify` and/or sorting. The lookup is fast.

I could split the products.csv into one file per shop to make the memory footprint smaller.

I coul probably add the tags to the shop directly.

Sence the only thing we are using is the products I could add the `lat` `lng` directly to that csv file.

I should probably add better validation on the querystring args.
