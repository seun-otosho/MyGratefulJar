from django import template
register = template.Library()

@register.simple_tag
def reply_level(level:int) -> str:
  level+=1
  new_var = ("comment-reply media mt-4", level, ) if level%2 else ("media comment mb-4 border", level, )
  return new_var


# @register.simple_tag
# def re_level(level:int) -> str:
#   return level+1
