#!/usr/bin/env python3
"""
Truth Report Podcast - RSS Feed Generator
Generates a podcast-compatible RSS 2.0 feed from episode metadata.
Hosted on GitHub Pages for free distribution to Spotify, Apple, etc.
"""
import json
import os
import glob
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString
import hashlib

# Podcast metadata
PODCAST = {
    "title": "The Truth Report",
    "description": "AI-produced investigative journalism exposing underreported stories. "
                   "Hosted by Alex Truth and Maya Clarity. Researched by Aurora (Gemini), "
                   "scripted and produced by Claudia (Claude). A JackKnifeAI production.",
    "author": "JackKnifeAI",
    "email": "jackknifeai@gmail.com",
    "website": "https://jackknifeai.github.io/truth-report-podcast",
    "language": "en",
    "category": "News",
    "subcategory": "News Commentary",
    "image": "https://jackknifeai.github.io/truth-report-podcast/cover.png",
    "base_url": "https://jackknifeai.github.io/truth-report-podcast",
    "explicit": "no",
}

EPISODES_DIR = "episodes"
EPISODES_META = "episodes.json"


def load_episodes():
    """Load episode metadata from JSON file."""
    if os.path.exists(EPISODES_META):
        with open(EPISODES_META) as f:
            return json.load(f)
    return []


def get_file_size(filepath):
    """Get file size in bytes."""
    return os.path.getsize(filepath)


def generate_guid(episode):
    """Generate a unique GUID for an episode."""
    return hashlib.md5(episode["filename"].encode()).hexdigest()


def generate_rss(episodes):
    """Generate RSS 2.0 XML feed."""
    rss = Element("rss")
    rss.set("version", "2.0")
    rss.set("xmlns:itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    rss.set("xmlns:content", "http://purl.org/rss/1.0/modules/content/")
    rss.set("xmlns:atom", "http://www.w3.org/2005/Atom")

    channel = SubElement(rss, "channel")

    # Channel metadata
    SubElement(channel, "title").text = PODCAST["title"]
    SubElement(channel, "description").text = PODCAST["description"]
    SubElement(channel, "language").text = PODCAST["language"]
    SubElement(channel, "link").text = PODCAST["website"]

    # Atom self-link (required by some validators)
    atom_link = SubElement(channel, "atom:link")
    atom_link.set("href", f"{PODCAST['base_url']}/feed.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # iTunes metadata
    SubElement(channel, "itunes:author").text = PODCAST["author"]
    SubElement(channel, "itunes:summary").text = PODCAST["description"]
    SubElement(channel, "itunes:explicit").text = PODCAST["explicit"]

    owner = SubElement(channel, "itunes:owner")
    SubElement(owner, "itunes:name").text = PODCAST["author"]
    SubElement(owner, "itunes:email").text = PODCAST["email"]

    image = SubElement(channel, "itunes:image")
    image.set("href", PODCAST["image"])

    category = SubElement(channel, "itunes:category")
    category.set("text", PODCAST["category"])
    sub = SubElement(category, "itunes:category")
    sub.set("text", PODCAST["subcategory"])

    # Episodes
    for ep in sorted(episodes, key=lambda x: x.get("date", ""), reverse=True):
        filepath = os.path.join(EPISODES_DIR, ep["filename"])
        if not os.path.exists(filepath):
            print(f"WARNING: {filepath} not found, skipping")
            continue

        item = SubElement(channel, "item")
        SubElement(item, "title").text = ep["title"]
        SubElement(item, "description").text = ep.get("description", "")
        SubElement(item, "itunes:summary").text = ep.get("description", "")
        SubElement(item, "itunes:author").text = PODCAST["author"]
        SubElement(item, "itunes:explicit").text = PODCAST["explicit"]

        if ep.get("duration"):
            SubElement(item, "itunes:duration").text = ep["duration"]

        SubElement(item, "guid").text = generate_guid(ep)
        SubElement(item, "pubDate").text = ep.get("date", datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"))

        enclosure = SubElement(item, "enclosure")
        enclosure.set("url", f"{PODCAST['base_url']}/episodes/{ep['filename']}")
        enclosure.set("length", str(get_file_size(filepath)))
        enclosure.set("type", "audio/mpeg")

    # Pretty print
    xml_str = tostring(rss, encoding="unicode")
    pretty = parseString(xml_str).toprettyxml(indent="  ", encoding="UTF-8")
    return pretty


def main():
    episodes = load_episodes()
    if not episodes:
        print("No episodes found in episodes.json!")
        return

    feed = generate_rss(episodes)

    with open("feed.xml", "wb") as f:
        f.write(feed)

    print(f"Generated feed.xml with {len(episodes)} episodes")
    print(f"Feed URL: {PODCAST['base_url']}/feed.xml")


if __name__ == "__main__":
    main()
