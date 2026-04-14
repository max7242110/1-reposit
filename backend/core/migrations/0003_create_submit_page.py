"""Создаём начальную страницу «Добавить кондиционер в рейтинг»."""

from django.db import migrations

SUBMIT_CONTENT = """\
<p>
  Хотите, чтобы ваш кондиционер попал в независимый рейтинг
  <strong>«Август-климат»</strong>? Мы готовы протестировать любую модель
  и опубликовать объективные результаты.
</p>

<h2>Как это работает</h2>
<ol>
  <li>Заполните короткую заявку по ссылке ниже — укажите бренд, модель и ваши контактные данные.</li>
  <li>Мы свяжемся с вами для уточнения деталей и согласования условий.</li>
  <li>Проведём независимое тестирование по нашей методике: замерим уровень шума, вибрацию,
      проверим комплектующие и функциональность.</li>
  <li>Результаты появятся в рейтинге — со всеми измерениями и итоговым индексом.</li>
</ol>

<h2>Что мы оцениваем</h2>
<p>
  Каждая модель проходит проверку по более чем 30 параметрам: от площади теплообменников
  и мощности компрессора до наличия Wi-Fi и функции самоочистки. Подробнее о методике —
  на странице <a href="/methodology">«Методика рейтинга»</a>.
</p>

<h2>Оставить заявку</h2>
<p>
  Заполните форму, и мы свяжемся с вами в течение нескольких рабочих дней:
</p>
<p>
  <a href="https://forms.google.com/" target="_blank" rel="noopener noreferrer"
     style="display:inline-block;padding:12px 24px;background:#2563eb;color:#fff;border-radius:8px;text-decoration:none;font-weight:600;">
    Заполнить заявку
  </a>
</p>
<p style="margin-top:8px;font-size:0.9em;color:#6b7280;">
  Ссылка на Google-форму. Администратор может изменить её в
  <a href="/admin/core/page/">панели управления</a>.
</p>
"""


def forwards(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Page.objects.get_or_create(
        slug="submit",
        defaults={
            "title_ru": "Добавить кондиционер в рейтинг",
            "content_ru": SUBMIT_CONTENT,
        },
    )


def backwards(apps, schema_editor):
    Page = apps.get_model("core", "Page")
    Page.objects.filter(slug="submit").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_page_model"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
