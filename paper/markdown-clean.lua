-- Keep the compiled Markdown reader usable in Obsidian.
function Span(el)
  return el.content
end

function Div(el)
  local blocks = pandoc.List()
  if el.identifier ~= '' then
    blocks:insert(pandoc.RawBlock('html', '<a id="' .. el.identifier .. '"></a>'))
  end
  blocks:extend(el.content)
  return blocks
end
