import json
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import concurrent.futures
from threading import Lock

from Helpers.SqlLiteHelper import SQLiteHelper
from Models.CatalogModel import Catalog
from Models.CatalogResponseModel import CatalogResponse
from Models.ExcelFileModel import ExcelFile
from Models.ImageModel import ImageModel
from Models.Part import Part
from Models.Parts import Parts
from Models.SectionsModel import Sections


class SnapperScraper:
    def __init__(self):
        self._catalogs = self._get_catalogs(
            path=os.path.join(os.getcwd(), "GetAssembly.json")
        )
        self._sections_url = "https://partstream.arinet.com/Parts/GetAssembly?cb=jsonp1721299421696&arib=SNP&aria={aria_id}&includeImgs=true&responsive=true&imgIsThmb=true&arik=uQyW0VZwE6romlteg2HI&aril=en-US&ariv=https%253A%252F%252Fwww.snapper.parts%252Fsnapper-parts-lookup"
        self._parts_url = "https://partstream.arinet.com/Parts/GetDetails?responsive=true&arik=uQyW0VZwE6romlteg2HI&aril=en-US&cb=jsonp1721320826060&ariq={ariq_slug}&ariv=https%253A%252F%252Fwww.snapper.parts%252Fsnapper-parts-lookup%253Faribrand%253DSNP"
        self._latest_model_code = 64974
        self._sql_helper = SQLiteHelper("SnapperDb.db")
        self._images = []
        self._max_workers = 10
        self.excel_lock = Lock()

    def scrape_data(self):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self._max_workers
        ) as executor:
            future_to_param = [
                executor.submit(self._scrape_catalog, item) for item in self._catalogs
            ]
            for future in concurrent.futures.as_completed(future_to_param):
                future.result()
        self._save_json([image.model_dump() for image in self._images], "images.json")

    def _scrape_catalog(self, item: CatalogResponse):
        c_data = self._recursive(aria_id=item.attr.aria, data=item.data)
        records = self._create_records(catalog_list=c_data)
        self._sql_helper._insert_many_records(records=records)
        image = self._get_all_images(catalog_list=c_data)
        self._images.extend(image)
        self._creatingExcelFile(catalog_list=c_data, section=item.data)

    def _recursive(self, aria_id: str, data: str = "") -> list[Catalog]:
        c_data: list[Catalog] = []
        response = requests.get(self._sections_url.format(aria_id=aria_id))
        if response.status_code == 200:
            data_from_catalog = self._parse_json_response(response_text=response.text)
            response_model = CatalogResponse(**data_from_catalog)
            closed_state, open_state = self._get_catalogs_by_state(
                data_from_catalog=response_model.model
            )
            for item in closed_state.json:
                new_list = self._recursive(aria_id=item.attr.aria, data=item.data)
                print(f"Item added {item.data}")
                c_data.extend(new_list)
            if open_state.json:
                sgl_code = self._resolve_sgl_code()
                parts_list = self._scrape_parts(
                    open_states=open_state.json, sgl_code=sgl_code
                )
                catalog = Catalog(catalog=data, sgl_code=sgl_code, sections=parts_list)
                c_data.append(catalog)
        else:
            print(f"Response error at arai id : {aria_id} data : {data}")
        return c_data

    def _resolve_sgl_code(self) -> str:
        sgl_code = f"SGL{self._latest_model_code:010}"
        self._latest_model_code += 1
        return sgl_code

    def _scrape_parts(self, open_states: Sections, sgl_code: str) -> list[Parts]:
        parts_list: list[Parts] = []
        for item in open_states:
            part = self._scrape_part(ariq_slug=item.attr.slug, sgl_code=sgl_code)
            if part:
                parts_list.append(part)
        return parts_list

    def _scrape_part(self, ariq_slug: str, sgl_code: str) -> Parts:
        response = requests.get(self._parts_url.format(ariq_slug=ariq_slug))
        if response.status_code != 200:
            print(f"Error at slug : {ariq_slug}")
            return None
        cleaned_response = SnapperScraper._parse_json_response(response.text)
        if cleaned_response["model"] and "error" in cleaned_response["model"]:
            return
        catalog_response = CatalogResponse(**cleaned_response)
        soup = BeautifulSoup(catalog_response.html, "html.parser")
        self._save_soup(soup)
        section = soup.select_one(
            "div[class=ari-assembly-detail] div[id=ariparts_assemblyDescription]"
        ).text.strip()
        image_url = soup.select_one("img[id=ariparts_image]").get("src")
        part_elements = soup.select(
            "div[class=ari-assembly-detail] div[id=ariPartList] ul li"
        )
        image_filename = f"{sgl_code}-{section}.jpg"
        sanitized_filename = self._sanitize_filename(image_filename)
        all_parts: list[Part] = []
        for part in part_elements:
            part_number = part.select_one(
                "div[class=ariPriceColumn] div[class=ariPLSku] div[class=ariPLSku]"
            ).text.strip()
            item_number = (
                part.select_one("div[class=ariPLTag]").text.replace("Ref:", "").strip()
            )
            description = part.select_one("div[class=ariPLDesc]").text.strip()
            partData = Part(
                part_number=part_number,
                item_number=item_number,
                description=description,
            )
            all_parts.append(partData)

        return Parts(
            section=section,
            section_diagram_url=image_url,
            section_diagram=sanitized_filename,
            parts=all_parts,
        )

    def _creatingExcelFile(self, catalog_list: list[Catalog], section: str):
        excel_models = []
        for catalog in catalog_list:
            model = ExcelFile(
                sgl_code=catalog.sgl_code,
                manufacturer="Snapper",
                model=catalog.catalog,
                unique_product_code=catalog.catalog,
                year="",
                section=section,
            ).model_dump()
            excel_models.append(model)

        df = pd.DataFrame(excel_models)
        df.rename(
            columns={
                "sgl_code": "SGL Code",
                "manufacturer": "Manufacturer",
                "model": "Model",
                "unique_product_code": "Unique Product Code",
                "year": "Year",
                "section": "Section",
            },
            inplace=True,
        )

        file_path = "ModelList.xlsx"

        with self.excel_lock:
            if os.path.exists(file_path):
                existing_df = pd.read_excel(file_path)
                combined_df = pd.concat([existing_df, df], ignore_index=True)
            else:
                combined_df = df

            combined_df.to_excel(
                file_path,
                index=False,
                columns=[
                    "SGL Code",
                    "Manufacturer",
                    "Model",
                    "Unique Product Code",
                    "Year",
                    "Section",
                ],
            )
            print(f"Excel file updated at {file_path}")

    def _save_soup(self, soup: BeautifulSoup):
        with open("soup.html", "w") as soup_file:
            soup_file.write(soup.prettify())

    def _save_json(self, json_data, file_name="json_data.json"):
        with open(file_name, "w") as json_file:
            json_file.write(json.dumps(json_data, indent=4))

    def _create_records(self, catalog_list: list[Catalog]) -> list[dict]:
        records = []
        for catalog in catalog_list:
            for section in catalog.sections:
                for part in section.parts:
                    record = {
                        "sgl_unique_model_code": catalog.sgl_code,
                        "section": section.section,
                        "part_number": part.part_number,
                        "description": part.description,
                        "item_number": part.item_number,
                        "section_diagram": section.section_diagram,
                    }
                    records.append(record)
        return records

    @staticmethod
    def _get_all_images(catalog_list: list[Catalog]):
        images: list[ImageModel] = []
        for catalog in catalog_list:
            for section in catalog.sections:
                images.append(
                    ImageModel(
                        file_name=section.section_diagram,
                        image_url=section.section_diagram_url,
                    )
                )
        return images

    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """
        Convert invalid filenames to valid filenames by replacing or removing invalid characters.
        """
        invalid_chars = r'[<>:"/\\|?*\']'
        sanitized_filename = re.sub(invalid_chars, "_", filename)
        sanitized_filename = sanitized_filename.strip()
        sanitized_filename = sanitized_filename[:255]
        return sanitized_filename

    @staticmethod
    def _parse_json_response(response_text: str) -> dict:
        start_idx = response_text.find("{")
        end_idx = response_text.rfind("}")
        json_data = response_text[start_idx : end_idx + 1]
        return json.loads(json_data)

    @staticmethod
    def _get_catalogs(path: str) -> CatalogResponse:
        with open(path, "r") as catalogs_file:
            json_data = json.load(catalogs_file)
            return CatalogResponse(**json_data).model.json

    @staticmethod
    def _get_catalogs_by_state(data_from_catalog: Sections) -> list[Sections]:
        closed_catalogs: Sections = Sections(json=[])
        open_catalogs: Sections = Sections(json=[])
        for item in data_from_catalog.json:
            (
                closed_catalogs.json.append(item)
                if item.state == "closed"
                else open_catalogs.json.append(item)
            )
        return closed_catalogs, open_catalogs
