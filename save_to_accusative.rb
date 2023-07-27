require 'petrovich'

def inflect_to_accusative(name)
  Petrovich(firstname: name).accusative.to_s
end

input_name = gets.chomp
accusative_name = inflect_to_accusative(input_name)
puts accusative_name
