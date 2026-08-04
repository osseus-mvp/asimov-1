# Datasheet attribution

Vendor documents behind the component-level entries in
[../../tests/requirements/requirements.yaml](../../tests/requirements/requirements.yaml).

Every document is recorded with its source URL, publisher, retrieval date and
sha256. **Only one is redistributed here.** The rest are recorded as a URL and
a hash, because their publishers grant no licence to republish them. A hash
without a file is still useful: it says exactly which revision a requirement's
number was read from, and it fails loudly if the vendor silently reissues the
document at the same URL.

Retrieval date for everything below: **2026-08-04**, UTC.

## Redistributed

| File | Part | Publisher | Revision | sha256 |
|---|---|---|---|---|
| `radxa_cm5_product_brief.pdf` | Radxa CM5 | Radxa Computer (Shenzhen) Co., Ltd. | 1.3, 2024-09-04 | `ef2b18c50a978c1ee1fdd7fe35e3f5bab6a946353406e1b3b38c4428164dd33f` |

Source: <https://dl.radxa.com/cm5/radxa_cm5_product_brief.pdf>

**This one is a judgement call and should be confirmed.** The PDF carries no
licence or copyright notice in its own text — only a "Radxa Computer
(Shenzhen) Co., Ltd." page footer and PDF metadata naming Radxa Limited as
creator. The basis for redistributing it is that Radxa licenses its
documentation under CC BY 4.0: the footer of
<https://docs.radxa.com/en/som/cm/cm5/download>, the page that links this file,
reads "Radxa-docs© 2026 by Radxa Computer (Shenzhen) Co.,Ltd. is licensed under
CC BY 4.0". That statement names the docs site rather than this PDF on
`dl.radxa.com`, so the licence is inherited rather than stated. Attribution is
given above as CC BY 4.0 requires. If that reading is wrong, delete the file
and leave the row.

Requirements reading this document: `REQ-L3-CM5-CAN-CONTROLLERS` (section 3
Specification, Connectivity: "Up to 3x CAN") and `REQ-L3-CM5-AVAILABILITY`
(section 8 Availability: "Radxa guarantees availability Radxa CM5 until at
least September 2032").

## Recorded, not redistributed — Encos joint modules

Five motors, one per actuated leg joint type. Retrieved from the
manufacturer's own product pages at `www.encos.cn` via the datasheet-download
link on each (数据手册下载).

Publisher: 南京因克斯智能科技有限公司 / Nanjing Encos Intelligent Technology
Co., Ltd. Not redistributed: the site footer reads 版权所有© 南京因克斯智能科技有限公司
("copyright, all rights reserved") and neither the site nor the documents grant
any licence to republish. Each PDF is the Chinese-language single-product
datasheet, five or six pages, with specification table, torque curves and
thermal-rise tables.

| Part | Joint | Pages | Product page | sha256 |
|---|---|---|---|---|
| EC-A6416-P2-25 | Hip pitch | 6 | [productinfo/57096](https://www.encos.cn/productinfo/57096.html?templateId=6217) → [filedownload/3040204](https://www.encos.cn/filedownload/3040204) | `85d627f5332aa8e8f4ca55c57191d884a9f441bd73375c5c41de7459884d1c9e` |
| EC-A5013-H17-100 | Hip roll | 6 | [productinfo/55393](https://www.encos.cn/productinfo/55393.html?templateId=6217) → [filedownload/3040237](https://www.encos.cn/filedownload/3040237) | `dbcaab87c520431a783e440757da7d4a53a212e6d98c8a77b9d591b5e8fc94fc` |
| EC-A3814-H14-107 | Hip yaw | 6 | [productinfo/55392](https://www.encos.cn/productinfo/55392.html?templateId=6217) → [filedownload/3040236](https://www.encos.cn/filedownload/3040236) | `5e84334b25e247aaf4bf4e4ea0af8b3d44ae1ab88db094c3afd38360459287a0` |
| EC-A4315-P2-36 | Knee | 5 | [productinfo/55373](https://www.encos.cn/productinfo/55373.html?templateId=6217) → [filedownload/3040202](https://www.encos.cn/filedownload/3040202) | `305dc469ca2d07feb06725e206a449fd576ece1a7c18bf48c517d0043c1eef1c` |
| EC-A4310-P2-36 | Ankle pitch, ankle roll | 5 | [productinfo/57543](https://www.encos.cn/productinfo/57543.html?templateId=6217) → [filedownload/3040201](https://www.encos.cn/filedownload/3040201) | `36deb9352e2ab391b5c3a12abfa2c35a33e8d126c9c3d35f0388276a66415751` |

A combined multi-motor catalogue by the same publisher, 电机数据手册 ("motor
datasheet"), is also on record. It covers EC-A4310-P2-36 and six motors this
robot does not use, and is included because it is an independently hosted copy
of the same vendor's numbers: 32 pages,
<https://www.worldrobotconference.com/uploads/exuser2024/video/8kgvba.pdf>,
sha256 `c367b4e0df52cd1beb6bfc0ca4d85abface7c20ce57a9f863e345ad8d68ca677`,
uploaded to the World Robot Conference exhibitor area. Same terms, not
redistributed.

## Recorded, not redistributed, and not retrieved — STMicroelectronics LSM6DSV

The 6-axis IMU `electrical/README.md` places at the bottom of the Motion
Control Board.

- Document: LSM6DSV datasheet, **DS13476 rev 5, August 2023**
- Publisher: STMicroelectronics
- Source: <https://www.st.com/resource/en/datasheet/lsm6dsv.pdf>
- sha256: **not recorded**

Two separate reasons, and both are stated because either alone would be enough.

**Not redistributable.** The document's own IMPORTANT NOTICE reads "No licence,
express or implied, to any intellectual property right is granted by ST
herein", and it closes "© 2023 STMicroelectronics – All rights reserved".

**Not retrieved.** `www.st.com` was unreachable from the network this record
was assembled on — HTTP/2 streams reset immediately and HTTP/1.1 requests timed
out, for the product page as well as the PDF. Rather than hash a copy from a
third-party mirror and label it with ST's URL, no hash is recorded. Anyone with
access to st.com should download the file and fill the field in.

The values `REQ-L3-IMU-TEMPERATURE-MIN` reads (operating temperature range -40
to +85 °C, section 4.1, parameter Top) were read from the text of that document
and are correct as of rev 5, but the file itself is not on record here.

## Two discrepancies worth carrying rather than resolving

### The motors are Encos, not Synapticon

`asimovinc/asimov-mjlab` attributes these parts to Synapticon throughout:
`asimov_constants.py`'s docstring says "Motor specifications from Synapticon
datasheets", the asset README says "Motors are from Synapticon EC-A series",
and the damping note says "The Synapticon motors have a maximum KD of 5.0".

They are not Synapticon parts. Every EC-A part number above resolves to Nanjing
Encos, whose datasheets are linked in this file, and the Asimov project's own
manual agrees: <https://mintlify.wiki/asimovinc/asimov-v0/hardware/motors> is
headed "Detailed specifications for Encos motors used in Asimov bipedal legs"
and names Encos as the manufacturer with <http://encos.cn> as the supplier.
Synapticon's actual product line is ACTILINK-S / SOMANET Integro, rated 0.65 to
3.2 N·m continuous — two orders of magnitude below a 120 N·m hip.

Nothing here corrects the mjlab repository. The register cites the in-repo
motor table for its torque numbers and this file records who actually published
the datasheet behind them.

### Rated torque and rotor inertia disagree with the vendor

Peak torque agrees everywhere — vendor datasheet, mjlab asset README, and the
Asimov v0 manual all give 120 / 90 / 60 / 75 / 36 N·m. That agreement is why
`REQ-L2-EFFORT-*` and `REQ-L3-MOTOR-*-PEAK` carry peak torque and no register
entry carries a rated torque or a rotor inertia as its limit.

| Part | Peak (Nm) | Rated, vendor | Rated, mjlab README | Rotor inertia, vendor | Rotor inertia, mjlab README |
|---|---|---|---|---|---|
| EC-A6416-P2-25 | 120 | 40 | 55 | 104 kg·mm² | 104.395 kg·mm² |
| EC-A5013-H17-100 | 90 | 30 | 45 | 10 kg·mm² | 10.0 kg·mm² |
| EC-A3814-H14-107 | 60 | 20 | 30 | 3 kg·mm² | 3.0 kg·mm² |
| EC-A4315-P2-36 | 75 | 25 | 50 | 25 kg·mm² | 25.5 kg·mm² |
| EC-A4310-P2-36 | 36 | 12 | 18 | 19 kg·mm² | 18.2 kg·mm² |

All five rated torques differ, by between 50 and 100 percent. Three of the five
rotor inertias differ; the ankle is the largest gap, and carrying the vendor's
19 kg·mm² through `rotor × gear²` would give an armature of 0.0246 kg·m²
against the 0.0236 the model uses, a 4.2 percent deviation that
`REQ-L2-REFLECTED-INERTIA` would fail at its 0.5 percent tolerance.

The register does not pick a winner. `REQ-L2-REFLECTED-INERTIA` is checked
against the mjlab asset README, because the requirement it states is that the
constants agree with the table documenting them — an internal-consistency
promise the project can keep. Which of the two rotor inertias is physically
correct is a question for whoever specified the part, and it is written down
here so that it is asked rather than averaged away.

One more, smaller: the EC-A4310-P2-36 datasheet gives a rated voltage of 24 V
where the other four are 48 V.
