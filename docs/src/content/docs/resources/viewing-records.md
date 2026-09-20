---
title: Viewing records
description: The read-only record page — infolist, record title, header actions, and relation managers.
---

The view page at `{resource}/{id}` is the read-only face of a record: an [infolist](/infolists/overview/) of its values, header actions, and any relation managers the resource declares.

![Orbit resource view page (light)](/examples/light/resources/view-record.png)

![Orbit resource view page (dark)](/examples/dark/resources/view-record.png)

## The infolist

Configure what is shown with the resource's `infolist()` hook:

```python title="app/orbit/resources/post_resource.py"
class PostResource(Resource):
    model = Post
    record_title_attribute = "title"

    @classmethod
    def infolist(cls, infolist: Infolist) -> Infolist:
        return infolist.schema([
            TextEntry.make("title").weight("bold"),
            TextEntry.make("status").badge().color("success"),
            TextEntry.make("body").prose(),
            TextEntry.make("created_at").since().label("Published"),
        ])
```

Skip the hook and Orbit builds a fallback infolist from the form schema — every field as a read-only text entry — so a view page always shows something useful.

## Record title

The page heading is the record's title, resolved from `record_title_attribute`. When that attribute is empty Orbit falls back to `Post #12`, and when the resource declares nothing it uses the resource label. The same title becomes the last breadcrumb, so the trail reads **Orbit › Posts › Launch Orbit**.

## Header actions

Edit and Delete appear by default when the records are mutable, gated by `can_update` and `can_delete`. Deleting redirects back to the list page; on a resource with `soft_deletes = True`, restore and force-delete are available too.

## Relation managers

Managers with `render_on` set to `"view"` or `"both"` render underneath the infolist, each as a titled section with its own table:

```python
class PostResource(Resource):
    @classmethod
    def get_relations(cls) -> list[type]:
        return [CommentsRelationManager]
```

See [relation managers](/resources/managing-relationships/) for how rows are loaded and what the built-in actions do.

## Related pages

- [Infolists overview](/infolists/overview/) — every entry type
- [Editing records](/resources/editing-records/) — where the Edit action leads
- [Global search](/resources/global-search/) — results link straight to this page
