import json

from litemapy import Schematic, Region

banner_patterns = {"flo": ["minecraft:flower_banner_pattern", ["minecraft:oxeye_daisy", "minecraft:paper"]],
                   "cre": ["minecraft:creeper_banner_pattern", ["minecraft:creeper_head", "minecraft:paper"]],
                   "sku": ["minecraft:skull_banner_pattern", ["minecraft:wither_skeleton_skull", "minecraft:paper"]],
                   "moj": ["minecraft:mojang_banner_pattern", ["minecraft:enchanted_golden_apple", "minecraft:paper"]],
                   "pig": ["minecraft:piglin_banner_pattern"],
                   "glb": ["minecraft:globe_banner_pattern"],
                   "flw": ["minecraft:flow_banner_pattern"],
                   "gus": ["minecraft:guster_banner_pattern"],
                   0: ["minecraft:white_dye", "minecraft:lily_of_the_valley", "minecraft:bone_meal"],
                   1: ["minecraft:orange_dye", "minecraft:orange_tulip", "minecraft:torchflower",
                       ["minecraft:red_dye", "minecraft:yellow_dye"]],
                   2: ["minecraft:magenta_dye", "minecraft:allium", "minecraft:lilac",
                       ["minecraft:purple_dye", "minecraft:pink_dye"],
                       ["minecraft:blue_dye", "minecraft:red_dye", "minecraft:pink_dye"],
                       ["minecraft:blue_dye", "minecraft:red_dye", "minecraft:red_dye", "minecraft:white_dye"]],
                   3: ["minecraft:light_blue_dye", "minecraft:blue_orchid",
                       ["minecraft:blue_dye", "minecraft:white_dye"]],
                   4: ["minecraft:yellow_dye", "minecraft:dandelion", "minecraft:sunflower"],
                   5: ["minecraft:lime_dye", ["minecraft:green_dye", "minecraft:white_dye"]],
                   6: ["minecraft:pink_dye", "minecraft:pink_tulip", "minecraft:pink_petals", "minecraft:peony",
                       ["minecraft:red_dye", "minecraft:white_dye"]],
                   7: ["minecraft:gray_dye", ["minecraft:black_dye", "minecraft:white_dye"]],
                   8: ["minecraft:light_gray_dye", "minecraft:azure_bluet", "minecraft:oxeye_daisy",
                       "minecraft:white_tulip", ["minecraft:black_dye", "minecraft:white_dye", "minecraft:white_dye"],
                       ["minecraft:gray_dye", "minecraft:white_dye"]],
                   9: ["minecraft:cyan_dye", ["minecraft:blue_dye", "minecraft:green_dye"], "minecraft:pitcher_plant"],
                   10: ["minecraft:purple_dye", ["minecraft:blue_dye", "minecraft:red_dye"]],
                   11: ["minecraft:blue_dye", "minecraft:lapis_lazuli", "minecraft:cornflower"],
                   12: ["minecraft:brown_dye", "minecraft:cocoa_beans"],
                   13: ["minecraft:green_dye", "minecraft:cactus"],
                   14: ["minecraft:red_dye", "minecraft:poppy", "minecraft:red_tulip", "minecraft:beetroot",
                        "minecraft:rose_bush"],
                   15: ["minecraft:black_dye", "minecraft:ink_sac", "minecraft:wither_rose"]}


def get_resources(schem: Schematic, *, get_storage_items: bool = True, storages: list[str] = None,
                  include_banner_dependencies: bool = False) -> list[
    dict[str, str | int | list[dict[str, str | int]]]]:
    blocks = {}
    storage_items = {}
    api_blocks = []
    for reg in list(schem.regions.values()):
        reg: Region
        reg.block_positions()
        for coords in reg.block_positions():
            b = reg[*coords]
            if b.id != "minecraft:air":
                if "banner" in b.id and "pattern" not in b.id:
                    if blocks.get(b.id, None) is None:
                        blocks[b.id] = {"count": 1}
                        if include_banner_dependencies:
                            if blocks[b.id].get("dependencies", None) is None:
                                blocks[b.id]["dependencies"] = []
                            dependencies = []
                            for tile_entity in reg.tile_entities:
                                if str(tile_entity.data["id"]) == "minecraft:banner":
                                    if tile_entity.data["x"] == coords[0] and tile_entity.data["y"] == coords[1] and \
                                            tile_entity.data["z"] == coords[2]:
                                        for pattern in tile_entity.data["Patterns"]:
                                            dependencies.append(banner_patterns[int(pattern["Color"])])
                                            if str(pattern["Pattern"]) in banner_patterns: dependencies.append(
                                                banner_patterns[str(pattern["Pattern"])])
                                        break
                            blocks[b.id]["dependencies"] = blocks[b.id]["dependencies"] + dependencies
                    else:
                        blocks[b.id]["count"] += 1
                else:
                    if blocks.get(b.id, None) is None:
                        blocks[b.id] = 1
                    else:
                        blocks[b.id] += 1
        for tile_entity in reg.tile_entities:
            items = tile_entity.data.get("Items", None)
            if get_storage_items:
                if items is not None:
                    for item in items:
                        tag = item.get("tag", None)
                        if tag is not None and (
                                str(tile_entity.data["id"]) in storages if storages is not None else True):
                            block_entity_tag = tag.get("BlockEntityTag", None)
                            stored_enchantments = tag.get("StoredEnchantments", None)
                            enchantments = tag.get("Enchantments", None)
                            title = tag.get("title", None)
                            if block_entity_tag is not None:
                                block_entity_items = block_entity_tag.get("Items", None)
                                if block_entity_items is not None:
                                    for block_entity_item in block_entity_items:
                                        if storage_items.get(block_entity_item["id"], None) is None:
                                            storage_items[str(block_entity_item["id"])] = int(
                                                block_entity_item["Count"])
                                        else:
                                            storage_items[str(block_entity_item["id"])] += int(
                                                block_entity_item["Count"])
                            if stored_enchantments is not None:
                                enchs = []
                                for enchantment in stored_enchantments:
                                    ench = {"id": str(enchantment["id"]), "level": int(enchantment["lvl"])}
                                    enchs.append(ench)
                                item["id"] = json.dumps({"id": str(item["id"]), "enchantments": enchs})
                            if enchantments is not None:
                                enchs = []
                                for enchantment in enchantments:
                                    ench = {"id": str(enchantment["id"]), "level": int(enchantment["lvl"])}
                                    enchs.append(ench)
                                item["id"] = json.dumps({"id": str(item["id"]), "enchantments": enchs})
                            if title is not None:
                                item["id"] = json.dumps(
                                    {"id": str(item["id"]), "title": str(title), "pages": tag.get("pages")})
                        if storage_items.get(item["id"], None) is None:
                            storage_items[str(item["id"])] = int(item["Count"])
                        else:
                            storage_items[str(item["id"])] += int(item["Count"])

    for item_id, count in blocks.items():
        if isinstance(count, dict):
            d = {"id": item_id, "type": "block"}
            d.update(count)
            api_blocks.append(d)
        else:
            api_blocks.append({"id": item_id, "count": count, "type": "block"})

    for item_id, count in storage_items.items():
        try:
            item_data = json.loads(item_id)
            item = {"id": item_data["id"], "count": count, "type": "storage_item"}
            if "enchantments" in item_data:
                item["enchantments"] = item_data["enchantments"]
            if "title" in item_data:
                item["book"] = {}
                item["book"]["title"] = item_data["title"]
                item["book"]["pages"] = []
                for page in item_data["pages"]:
                    item["book"]["pages"].append(json.loads(page))
            api_blocks.append(item)
        except:
            item = {"id": item_id, "count": count, "type": "storage_item"}
            api_blocks.append(item)

    return api_blocks


print(get_resources(Schematic.load("bannerTest.litematic"), get_storage_items=True, storages=None,
                    include_banner_dependencies=True))
