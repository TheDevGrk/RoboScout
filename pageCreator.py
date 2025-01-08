import json
import streamlit as st

# store filters as session states when button is pressed since that is unique to device
# then here grab those session states, feed it to the filterInputs functions, take that output data, and create the page here
# should make it unique to each device in a pretty simple way

def createSearchPage():
    # with open(dataPath, "r") as data:
    print()

    # after page generation is done, redirect to the website/search page