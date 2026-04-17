"use client";

import { useMemo, useState } from "react";

import { ApiError, createSubmission } from "@/lib/api";
import { BrandOption } from "@/lib/types";

import Tooltip from "./Tooltip";

interface Props {
  brands: BrandOption[];
}

const DRAIN_PAN_HEATER_OPTIONS = [
  { value: "нет", label: "Нет" },
  { value: "тэн", label: "ТЭН" },
  { value: "термокабель", label: "Термокабель" },
];

const IONIZER_OPTIONS = [
  { value: "нет", label: "Нет" },
  { value: "щётка", label: "Щётка" },
  { value: "отдельный прибор", label: "Отдельный прибор" },
];

const RUSSIAN_REMOTE_OPTIONS = [
  { value: "нет", label: "Нет" },
  { value: "только корпус", label: "Только корпус" },
  { value: "корпус и экран", label: "Корпус + экран" },
];

const UV_LAMP_OPTIONS = [
  { value: "нет", label: "Нет" },
  { value: "мелкие светодиоды", label: "Мелкие светодиоды" },
  { value: "крупная лампа", label: "Крупная лампа" },
];

function HelpIcon({ tip }: { tip: string }) {
  return (
    <Tooltip text={tip}>
      <span className="inline-flex items-center justify-center w-4 h-4 ml-1 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-[10px] font-bold cursor-help align-middle">
        ?
      </span>
    </Tooltip>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mt-6 mb-3 first:mt-0">
      {children}
    </h3>
  );
}

function Label({
  children,
  required,
  tip,
}: {
  children: React.ReactNode;
  required?: boolean;
  tip?: string;
}) {
  return (
    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
      {children}
      {required && <span className="text-rose-600 ml-0.5">*</span>}
      {tip && <HelpIcon tip={tip} />}
    </label>
  );
}

const inputCls =
  "w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm text-gray-900 dark:text-white";

function computeArea(length: number, count: number, diameter: number): number {
  if (length > 0 && count > 0 && diameter > 0) {
    return Math.PI * diameter * length * count / 1_000_000;
  }
  return 0;
}

export default function SubmitForm({ brands }: Props) {
  // Identity
  const [brandId, setBrandId] = useState("");
  const [customBrand, setCustomBrand] = useState("");
  const [series, setSeries] = useState("");
  const [innerUnit, setInnerUnit] = useState("");
  const [outerUnit, setOuterUnit] = useState("");
  const [compressorModel, setCompressorModel] = useState("");
  const [nominalCapacity, setNominalCapacity] = useState("");
  const [price, setPrice] = useState("");

  // Boolean criteria
  const [drainPanHeater, setDrainPanHeater] = useState("нет");
  const [erv, setErv] = useState(false);
  const [fanSpeedOutdoor, setFanSpeedOutdoor] = useState(false);
  const [remoteBacklight, setRemoteBacklight] = useState(false);

  // Categorical / numeric criteria
  const [fanSpeedsIndoor, setFanSpeedsIndoor] = useState("");
  const [fineFilters, setFineFilters] = useState("0");
  const [ionizer, setIonizer] = useState("нет");
  const [russianRemote, setRussianRemote] = useState("нет");
  const [uvLamp, setUvLamp] = useState("нет");

  // Inner heat exchanger
  const [innerLength, setInnerLength] = useState("");
  const [innerTubeCount, setInnerTubeCount] = useState("");
  const [innerDiameter, setInnerDiameter] = useState("");

  // Outer heat exchanger
  const [outerLength, setOuterLength] = useState("");
  const [outerTubeCount, setOuterTubeCount] = useState("");
  const [outerDiameter, setOuterDiameter] = useState("");
  const [outerThickness, setOuterThickness] = useState("");

  // Evidence
  const [photos, setPhotos] = useState<File[]>([]);
  const [videoUrl, setVideoUrl] = useState("");

  // Links
  const [buyUrl, setBuyUrl] = useState("");
  const [supplierUrl, setSupplierUrl] = useState("");

  // Contact
  const [email, setEmail] = useState("");
  const [consent, setConsent] = useState(false);

  // Honeypot
  const [website, setWebsite] = useState("");

  // Status
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const innerArea = useMemo(
    () => computeArea(parseFloat(innerLength) || 0, parseInt(innerTubeCount) || 0, parseFloat(innerDiameter) || 0),
    [innerLength, innerTubeCount, innerDiameter],
  );

  const outerArea = useMemo(
    () => computeArea(parseFloat(outerLength) || 0, parseInt(outerTubeCount) || 0, parseFloat(outerDiameter) || 0),
    [outerLength, outerTubeCount, outerDiameter],
  );

  function handlePhotos(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (files) {
      setPhotos(Array.from(files));
    }
  }

  function removePhoto(idx: number) {
    setPhotos((prev) => prev.filter((_, i) => i !== idx));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg("");

    if (!innerUnit.trim() || !outerUnit.trim() || !compressorModel.trim()) {
      setStatus("error");
      setErrorMsg("Заполните обязательные поля модели.");
      return;
    }
    if (!brandId && !customBrand.trim()) {
      setStatus("error");
      setErrorMsg("Укажите бренд.");
      return;
    }
    if (!nominalCapacity || parseFloat(nominalCapacity) <= 0) {
      setStatus("error");
      setErrorMsg("Укажите номинальную холодопроизводительность.");
      return;
    }
    if (!fanSpeedsIndoor || parseInt(fanSpeedsIndoor) < 1) {
      setStatus("error");
      setErrorMsg("Укажите количество скоростей вентилятора.");
      return;
    }
    if (photos.length === 0) {
      setStatus("error");
      setErrorMsg("Загрузите хотя бы одно фото измерений.");
      return;
    }
    if (!email.trim()) {
      setStatus("error");
      setErrorMsg("Укажите e-mail.");
      return;
    }
    if (!consent) {
      setStatus("error");
      setErrorMsg("Необходимо согласие на обработку персональных данных.");
      return;
    }

    const data: Record<string, string | number | boolean> = {
      inner_unit: innerUnit.trim(),
      outer_unit: outerUnit.trim(),
      compressor_model: compressorModel.trim(),
      nominal_capacity_watt: parseFloat(nominalCapacity),
      drain_pan_heater: drainPanHeater,
      erv,
      fan_speed_outdoor: fanSpeedOutdoor,
      remote_backlight: remoteBacklight,
      fan_speeds_indoor: parseInt(fanSpeedsIndoor),
      fine_filters: parseInt(fineFilters),
      ionizer_type: ionizer,
      russian_remote: russianRemote,
      uv_lamp: uvLamp,
      inner_he_length_mm: parseFloat(innerLength) || 0,
      inner_he_tube_count: parseInt(innerTubeCount) || 0,
      inner_he_tube_diameter_mm: parseFloat(innerDiameter) || 0,
      outer_he_length_mm: parseFloat(outerLength) || 0,
      outer_he_tube_count: parseInt(outerTubeCount) || 0,
      outer_he_tube_diameter_mm: parseFloat(outerDiameter) || 0,
      outer_he_thickness_mm: parseFloat(outerThickness) || 0,
      submitter_email: email.trim(),
      consent: true,
      website,
    };

    if (brandId && brandId !== "other") data.brand = parseInt(brandId);
    if (customBrand.trim()) data.custom_brand_name = customBrand.trim();
    if (series.trim()) data.series = series.trim();
    if (price.trim()) data.price = parseFloat(price);
    if (videoUrl.trim()) data.video_url = videoUrl.trim();
    if (buyUrl.trim()) data.buy_url = buyUrl.trim();
    if (supplierUrl.trim()) data.supplier_url = supplierUrl.trim();

    setStatus("loading");
    try {
      await createSubmission(data, photos);
      setStatus("success");
    } catch (err) {
      setStatus("error");
      if (err instanceof ApiError) {
        setErrorMsg(
          err.status === 429
            ? "Слишком много заявок с вашего IP. Попробуйте позже."
            : `Ошибка отправки: ${err.message}`,
        );
      } else {
        setErrorMsg("Сетевая ошибка. Попробуйте позже.");
      }
    }
  }

  if (status === "success") {
    return (
      <div className="mt-8 p-6 rounded-xl bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-emerald-800 dark:text-emerald-300">
        <p className="text-lg font-semibold mb-2">Заявка отправлена!</p>
        <p className="text-sm">
          Спасибо! Ваша заявка будет рассмотрена администратором. После проверки
          кондиционер появится в рейтинге.
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-8 p-4 sm:p-6 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 space-y-4"
    >
      <h2 className="text-xl font-bold text-gray-900 dark:text-white">
        Заявка на добавление кондиционера
      </h2>

      {/* Honeypot */}
      <input
        type="text"
        name="website"
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
        value={website}
        onChange={(e) => setWebsite(e.target.value)}
        className="hidden"
      />

      {/* === Секция 1: Модель === */}
      <SectionTitle>Модель кондиционера</SectionTitle>

      <div>
        <Label required tip="Выберите бренд из списка. Если вашего бренда нет, выберите «Другой» и введите название.">
          Бренд
        </Label>
        <select
          value={brandId}
          onChange={(e) => {
            setBrandId(e.target.value);
            if (e.target.value !== "other") setCustomBrand("");
          }}
          className={inputCls}
          required
        >
          <option value="">Выберите бренд…</option>
          {brands.map((b) => (
            <option key={b.id} value={String(b.id)}>
              {b.name}
            </option>
          ))}
          <option value="other">Другой…</option>
        </select>
      </div>

      {brandId === "other" && (
        <div>
          <Label required>Название бренда</Label>
          <input
            type="text"
            value={customBrand}
            onChange={(e) => setCustomBrand(e.target.value)}
            className={inputCls}
            maxLength={255}
            required
          />
        </div>
      )}

      <div>
        <Label tip="Необязательное поле. Например «ZOOM» или «AURORA».">Серия</Label>
        <input type="text" value={series} onChange={(e) => setSeries(e.target.value)} className={inputCls} maxLength={255} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <Label required tip="Указана на шильдике внутреннего блока. Например: MSAG1-09HRN1">
            Модель внутреннего блока
          </Label>
          <input type="text" value={innerUnit} onChange={(e) => setInnerUnit(e.target.value)} className={inputCls} maxLength={255} required />
        </div>
        <div>
          <Label required tip="Указана на шильдике наружного блока.">Модель наружного блока</Label>
          <input type="text" value={outerUnit} onChange={(e) => setOuterUnit(e.target.value)} className={inputCls} maxLength={255} required />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <Label required tip="Указана на шильдике компрессора наружного блока. Например: QXC-19K">
            Модель компрессора
          </Label>
          <input type="text" value={compressorModel} onChange={(e) => setCompressorModel(e.target.value)} className={inputCls} maxLength={255} required />
        </div>
        <div>
          <Label required tip="Указана в характеристиках кондиционера. Типичные значения: 2050, 2640, 3520, 5280, 7030 Вт.">
            Холодопроизводительность (Вт)
          </Label>
          <input type="number" value={nominalCapacity} onChange={(e) => setNominalCapacity(e.target.value)} className={inputCls} min={1} step="1" required />
        </div>
      </div>

      <div>
        <Label tip="Рекомендованная розничная цена в рублях (необязательно).">Цена (руб.)</Label>
        <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} className={inputCls} min={0} step="0.01" />
      </div>

      {/* === Секция 2: Характеристики === */}
      <SectionTitle>Характеристики</SectionTitle>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-3">
          <div>
            <Label required tip="Наличие нагревательного элемента в поддоне наружного блока для обогрева в зимний период.">
              Обогрев поддона
            </Label>
            <select value={drainPanHeater} onChange={(e) => setDrainPanHeater(e.target.value)} className={inputCls}>
              {DRAIN_PAN_HEATER_OPTIONS.map((o) => (
                <option key={o.value} value={o.value}>{o.label}</option>
              ))}
            </select>
          </div>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input type="checkbox" checked={erv} onChange={(e) => setErv(e.target.checked)} className="rounded" />
            Наличие ЭРВ
            <HelpIcon tip="Электронный расширительный вентиль (ЭРВ) — более точное управление потоком хладагента по сравнению с капиллярной трубкой." />
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input type="checkbox" checked={fanSpeedOutdoor} onChange={(e) => setFanSpeedOutdoor(e.target.checked)} className="rounded" />
            Регулировка оборотов вент. наруж. блока
            <HelpIcon tip="Наличие или отсутствие регулировки оборотов." />
          </label>
          <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input type="checkbox" checked={remoteBacklight} onChange={(e) => setRemoteBacklight(e.target.checked)} className="rounded" />
            Подсветка экрана пульта
            <HelpIcon tip="Наличие подсветки дисплея на пульте дистанционного управления." />
          </label>
        </div>

        <div className="space-y-4">
          <div>
            <Label required tip="Количество скоростей вентилятора внутреннего блока (без учёта автоматического режима).">
              Кол-во скоростей вент. внутр. блока
            </Label>
            <input type="number" value={fanSpeedsIndoor} onChange={(e) => setFanSpeedsIndoor(e.target.value)} className={inputCls} min={1} max={100} required />
          </div>

          <div>
            <Label required tip="Количество фильтров тонкой очистки воздуха (помимо основного сетчатого фильтра).">
              Фильтры тонкой очистки
            </Label>
            <div className="flex gap-4 mt-1">
              {["0", "1", "2"].map((v) => (
                <label key={v} className="flex items-center gap-1 text-sm text-gray-700 dark:text-gray-300">
                  <input type="radio" name="fine_filters" value={v} checked={fineFilters === v} onChange={() => setFineFilters(v)} />
                  {v}
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <Label required tip="Тип ионизатора воздуха. Если ионизатора нет, выберите «Нет».">Ионизатор</Label>
          <select value={ionizer} onChange={(e) => setIonizer(e.target.value)} className={inputCls}>
            {IONIZER_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
        <div>
          <Label required tip="Наличие русского языка на пульте ДУ: на корпусе кнопок и/или на экране дисплея.">
            Русифицированный пульт
          </Label>
          <select value={russianRemote} onChange={(e) => setRussianRemote(e.target.value)} className={inputCls}>
            {RUSSIAN_REMOTE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
        <div>
          <Label required tip="Наличие ультрафиолетовой лампы для обеззараживания воздуха.">УФ-лампа</Label>
          <select value={uvLamp} onChange={(e) => setUvLamp(e.target.value)} className={inputCls}>
            {UV_LAMP_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* === Секция 3: Теплообменник внутр. блока === */}
      <SectionTitle>Теплообменник внутреннего блока</SectionTitle>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <Label required tip="Длина теплообменника (радиатора) внутреннего блока в миллиметрах. Измеряется рулеткой по длинной стороне.">
            Длина (мм)
          </Label>
          <input type="number" value={innerLength} onChange={(e) => setInnerLength(e.target.value)} className={inputCls} min={0} step="0.1" required />
        </div>
        <div>
          <Label required tip="Количество медных трубок в теплообменнике. Считается по торцу теплообменника.">
            Кол-во трубок
          </Label>
          <input type="number" value={innerTubeCount} onChange={(e) => setInnerTubeCount(e.target.value)} className={inputCls} min={1} required />
        </div>
        <div>
          <Label required tip="Наружный диаметр медных трубок в миллиметрах. Типичные значения: 5, 7 или 9 мм. Измеряется штангенциркулем.">
            Диаметр трубок (мм)
          </Label>
          <input type="number" value={innerDiameter} onChange={(e) => setInnerDiameter(e.target.value)} className={inputCls} min={0} step="0.01" required />
        </div>
      </div>

      {innerArea > 0 && (
        <div className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 px-4 py-2 rounded-lg">
          Рассчитанная площадь труб: <span className="font-semibold">{innerArea.toFixed(4)} м²</span>
        </div>
      )}

      {/* === Секция 4: Теплообменник наруж. блока === */}
      <SectionTitle>Теплообменник наружного блока</SectionTitle>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <Label required tip="Длина теплообменника наружного блока в миллиметрах.">
            Длина (мм)
          </Label>
          <input type="number" value={outerLength} onChange={(e) => setOuterLength(e.target.value)} className={inputCls} min={0} step="0.1" required />
        </div>
        <div>
          <Label required tip="Количество медных трубок в теплообменнике наружного блока.">
            Кол-во трубок
          </Label>
          <input type="number" value={outerTubeCount} onChange={(e) => setOuterTubeCount(e.target.value)} className={inputCls} min={1} required />
        </div>
        <div>
          <Label required tip="Наружный диаметр медных трубок теплообменника наружного блока в миллиметрах. Типичные значения: 5, 7 или 9 мм.">
            Диаметр трубок (мм)
          </Label>
          <input type="number" value={outerDiameter} onChange={(e) => setOuterDiameter(e.target.value)} className={inputCls} min={0} step="0.01" required />
        </div>
        <div>
          <Label required tip="Толщина теплообменника наружного блока в миллиметрах (глубина пакета ламелей).">
            Толщина (мм)
          </Label>
          <input type="number" value={outerThickness} onChange={(e) => setOuterThickness(e.target.value)} className={inputCls} min={0} step="0.1" required />
        </div>
      </div>

      {outerArea > 0 && (
        <div className="text-sm text-gray-600 dark:text-gray-400 bg-blue-50 dark:bg-blue-900/20 px-4 py-2 rounded-lg">
          Рассчитанная площадь труб: <span className="font-semibold">{outerArea.toFixed(4)} м²</span>
        </div>
      )}

      {/* === Секция 5: Подтверждение замеров === */}
      <SectionTitle>Подтверждение замеров</SectionTitle>

      <div>
        <Label required tip="Загрузите фотографии с результатами ваших измерений (шильдики, замеры рулеткой/штангенциркулем). Минимум 1 фото, максимум 20.">
          Фото измерений
        </Label>
        <input
          type="file"
          accept="image/*"
          multiple
          onChange={handlePhotos}
          className="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-blue-50 dark:file:bg-blue-900/30 file:text-blue-700 dark:file:text-blue-400 hover:file:bg-blue-100 dark:hover:file:bg-blue-900/50 file:cursor-pointer"
        />
        {photos.length > 0 && (
          <div className="flex flex-wrap gap-2 mt-3">
            {photos.map((f, i) => (
              <div key={i} className="relative group">
                <img
                  src={URL.createObjectURL(f)}
                  alt={f.name}
                  className="h-20 w-20 object-cover rounded-lg border border-gray-200 dark:border-gray-700"
                />
                <button
                  type="button"
                  onClick={() => removePhoto(i)}
                  className="absolute -top-1.5 -right-1.5 w-5 h-5 rounded-full bg-rose-600 text-white text-xs flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  x
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <Label tip="Ссылка на видео (YouTube, RuTube и т.д.), где вы демонстрируете процесс измерений.">
          Ссылка на видео измерений
        </Label>
        <input type="url" value={videoUrl} onChange={(e) => setVideoUrl(e.target.value)} className={inputCls} placeholder="https://..." />
      </div>

      {/* === Секция 6: Ссылки === */}
      <SectionTitle>Ссылки</SectionTitle>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <Label tip="Ссылка на страницу товара в интернет-магазине, где можно приобрести этот кондиционер.">
            Где купить
          </Label>
          <input type="url" value={buyUrl} onChange={(e) => setBuyUrl(e.target.value)} className={inputCls} placeholder="https://..." />
        </div>
        <div>
          <Label tip="Ссылка на официальный сайт производителя или дистрибьютора.">
            Сайт поставщика
          </Label>
          <input type="url" value={supplierUrl} onChange={(e) => setSupplierUrl(e.target.value)} className={inputCls} placeholder="https://..." />
        </div>
      </div>

      {/* === Секция 7: Контакт === */}
      <SectionTitle>Контакт</SectionTitle>

      <div>
        <Label required tip="На этот адрес вы получите уведомление о результате рассмотрения заявки.">
          E-mail
        </Label>
        <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputCls} required />
      </div>

      <label className="flex items-start gap-2 text-sm text-gray-700 dark:text-gray-300">
        <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} className="rounded mt-0.5" required />
        <span>
          Я даю согласие на обработку персональных данных в соответствии с{" "}
          <span className="text-gray-500">Федеральным законом №152-ФЗ «О персональных данных»</span>.
          <span className="text-rose-600 ml-0.5">*</span>
        </span>
      </label>

      {/* Ошибка */}
      {status === "error" && (
        <p className="text-sm text-rose-700 dark:text-rose-400">{errorMsg}</p>
      )}

      {/* Кнопка */}
      <div className="flex items-center justify-between gap-3 pt-2">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Заявка рассматривается администратором перед добавлением в рейтинг.
        </p>
        <button
          type="submit"
          disabled={status === "loading"}
          className="px-6 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors whitespace-nowrap"
        >
          {status === "loading" ? "Отправка…" : "Отправить заявку"}
        </button>
      </div>
    </form>
  );
}
