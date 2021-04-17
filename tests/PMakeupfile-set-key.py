# set_registry_in_current_user_as_string(
#     key_relative_to_root=r"SOFTWARE\Microsoft\Clipboard",
#     key="hello",
#     value="world"
# )


res = delete_registry_from_current_user(
   key_relative_to_root=r"SOFTWARE\Microsoft\Clipboard",
   key="hello",
)
echo(res)