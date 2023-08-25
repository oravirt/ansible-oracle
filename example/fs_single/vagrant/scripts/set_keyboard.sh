#!/usr/bin/env bash
function set_keyboard_layout ()
{

  echo "******************************************************************************"
  echo "Setting keyboard to ${THE_KEYBOARD} $(date)"
  echo "******************************************************************************"

# localectl list-keymaps
localectl set-keymap "${THE_KEYBOARD}"
localectl status
}

set_keyboard_layout