import tcod as libtcod


from game_messages import Message
from components.graphics import colors

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item_to_add):
        results = []

        if len(self.items) >= self.capacity:
            results.append({
                'item_added': None,
                'message': Message('You cannot carry any more, your inventory is full')
                })
        else:
            results.append({
                'item_added': item_to_add,
                'message': Message('You pick up {0} {1}!'.format(item_to_add.number,item_to_add.name), colors.get('green'))
            })


            item_added = False
            for item in self.items:
                if item.name == item_to_add.name:
                    item.number += item_to_add.number
                    item_added = True

            if not item_added:
                self.items.append(item_to_add)

        return results

    def use(self, item_entity, **kwargs):
        results = []

        item_component = item_entity.item

        if item_component.use_function is None:
            equippable_component = item_entity.equippable

            if equippable_component:
                results.append({'equip': item_entity})
            else:
                results.append({'message': Message('The {0} cannot be used'.format(item_entity.name), colors.get('red'))})
        else:
            if item_component.targeting and not (kwargs.get('target_x') or kwargs.get('target_y')):
                results.append({'targeting': item_entity})
            else:
                kwargs = {**item_component.function_kwargs, **kwargs}
                item_use_results = item_component.use_function(self.owner, **kwargs)

                for item_use_result in item_use_results:
                    if item_use_result.get('consumed'):
                        self.remove_item(item_entity)

                results.extend(item_use_results)

        return results

    def remove_item(self, item):
        if item.number > 1:
            item.number -= 1
        else:
            self.items.remove(item)

    def drop_item(self, item):
        results = []

        if self.owner.equipment.main_hand == item or self.owner.equipment.off_hand == item:
            self.owner.equipment.toggle_equip(item)

        item.x = self.owner.x
        item.y = self.owner.y

        self.remove_item(item)
        results.append({'item_dropped': item, 'message': Message('You dropped the {0}'.format(item.name),
                                                                 colors.get('dark'))})

        return results