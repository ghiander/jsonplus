# JSONplus

This repo is work in progress. The idea is to implement a library that allows loading/writing JSON files with annotations. This is particularly useful in scientific problems where data is often accompanied by metadata.

```
[{
    "name": "foo"
    "date": "2025-01-01"      # aggregation_method: latest
    "measure": 1.0            # significant_figures: 2
},
{
    "name": "bar"
    "date": "2024-01-01"      # earliest
    "measure": "2.0"          # significant figures: 1
}]
```

```
import jp

jp.load("mydata.json")
>>> <dictx: attributes=['name', 'date', 'measure']>
```
`jp.load()` also loads "mydata.meta.json" creating a `dictx` object, an extended dictionary made of `AugmentedValue` attributes, `AugmentedValue` objects contain two attributes, `data` and `metadata` where `metadata` is optional. This implementation forces `data` and `metadata` to stick together while operating on objects. For loading JSON arrays, `metadata` must be consistent in length, e.g., 3 data objects expect 3 metadata objects as these are merged by one-to-one matching. (The logic could have used indices but the corresponding `meta.json` file would have lost structural analogy with its data file). The serialiser (to be implemented) will therefore split the attributes to yield the corresponding `.json` and `.meta.json` files.


## TODO:
- [x] Deserialisation/obj creation logic
- [ ] Ensure consistency with `dict`
- [ ] Reader
- [ ] Unit tests for deserialisation
- [ ] Serialisation logic
- [ ] Writer
- [ ] Unit tests for serialisation
- [ ] Creation of package
- [ ] Docs
