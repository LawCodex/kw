# Kuwait — LawCodex (تشريعات دولة الكويت)

Kuwaiti legislation as plain Markdown, in Arabic. Part of [LawCodex](https://github.com/LawCodex):
one repository per jurisdiction.

> **Coverage is minimal.** No official source of Kuwaiti legislation could be used: each one was
> unreachable, blocked automated clients, or had terms of use that forbid republication (details
> below). This repository holds only the Constitution and one other law, taken from **Arabic
> Wikisource**, a volunteer, unofficial transcription. Check the official text (Kuwait Al-Youm,
> the Official Gazette) before you rely on them.

- Retrieved: **2026-10-13**

## Coverage

| File | Text | Status |
| --- | --- | --- |
| `ar/constitution/1962-constitution.md` | دستور دولة الكويت: the Constitution of 11 November 1962 (183 articles). It has never been amended. An Amiri Order of 10 May 2024 dissolved the National Assembly and suspended some articles for up to four years; that suspension is not reflected in the text. | in force |
| `ar/laws/1999/1999-64.md` | قانون رقم 64 لسنة 1999 في شأن حقوق الملكية الفكرية: Law No. 64 of 1999 on Intellectual Property Rights | repealed (replaced by Law No. 75 of 2019) |

Source pages: [دستور الكويت](https://ar.wikisource.org/wiki/دستور_الكويت) and
[قانون رقم 64 لسنة 1999 …](https://ar.wikisource.org/wiki/قانون_رقم_64_لسنة_1999_في_شأن_حقوق_الملكية_الفكرية_(الكويت)).
The front matter of each file records the Wikisource revision it was built from
(`source_revision`). The Wikisource transcription of the Constitution omits most hamzas
(e.g. "الاسلام" for "الإسلام"). It is reproduced as is.

## Sources examined and why they were not used

| Source | Finding |
| --- | --- |
| Kuwait National Assembly, [kna.kw](https://www.kna.kw) (Constitution, Rules of Procedure, legislation) | Reachable, but its terms of use (شروط الاستخدام) state: "لا يجوز إعادة إنتاج أو إعادة نشر أو تحميل أو عرض بشكل علني أو إرسال أو توزيع بأي شكل من الأشكال محتويات موقع مجلس الأمة بدون الحصول على موافقة خطية مسبقة من الأمانة العامة لمجلس الأمة" (no reproduction or republication without the Secretariat-General's prior written consent). Not used. Its former legislation database (`/clt-html5/`) no longer exists, and the Internet Archive holds no law texts from it. |
| Legal Advice and Legislation Department (إدارة الفتوى والتشريع), fatwa.gov.kw | Connection timed out. The Internet Archive holds only its library catalogue, not legislation texts. |
| Kuwait Government Online, [e.gov.kw](https://www.e.gov.kw) | Every request answered HTTP 403 by an Azure Application Gateway. The Internet Archive holds about 20 Arabic PDFs of individual laws from it (Commercial, Labour, Traffic, Customs, Tax and Copyright laws, among others), but the portal's terms of use could not be read (archived only as an image), so they were not used. |
| Ministry of Justice, moj.gov.kw | Reachable only intermittently (TLS resets). Its archived "Kuwait laws" folder contains only scanned treaty-approval laws. |
| Amiri Diwan, da.gov.kw | Describes the Constitution but does not publish its full text. |
| GCC Legal Information Network, gcc-legal.org | Unreachable (TLS failure); archive coverage sparse. |

To build a full Kuwaiti corpus, LawCodex would need either written consent from the National
Assembly Secretariat-General to republish the texts on kna.kw, or access to the Legal Advice and
Legislation Department's database (or its successor).

## Structure

```
ar/constitution/1962-constitution.md
ar/laws/<year>/<year>-<number>.md
```

Parts (الباب), chapters (الفصل) and sections (الفرع) are headings, and each article (المادة)
is a heading one level below.

## Licence

These are official texts of the State of Kuwait (legislation is generally excluded from copyright
protection). The transcriptions come from Wikisource (CC BY-SA 4.0 for any editorial
contribution); every file links its Wikisource page.

## Regenerating

```sh
pip install -r scripts/requirements.txt
python scripts/kw_wikisource.py /path/to/raw .
```
