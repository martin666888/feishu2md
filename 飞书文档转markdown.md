我的核心目标，基于飞书开放平台集成API，调用飞书运文档的document_id，解析其中所有的块，识别出正确的markdown语法，然后生成文档对应的markdown文件。
我的痛点，飞书文档自身有很好的markdown语法识别系统，但无法直接导出markdown文件，这也就造成我无法很方便的把我的文档进行传播。
但一个比较的好的地方是，飞书提供强大的后台API，可以让我创建飞书应用读取文档的所有块内容。
# 一个示例

我的一片飞书云文档链接如下：
https://tsaae9fgrn.feishu.cn/wiki/KREmwsK9LiuqYnk4ek5cX1eKnFx?fromScene=spaceOverview
我可以提取出其中的document_id：KREmwsK9LiuqYnk4ek5cX1eKnFx
放入如下代码：
```Python
import json
import lark_oapi as lark
from lark_oapi.api.docx.v1 import *

# SDK 使用说明: https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/server-side-sdk/python--sdk/preparations-before-development

# 以下示例代码默认根据文档示例值填充，如果存在代码问题，请在 API 调试台填上相关必要参数后再复制代码使用

def main():

    # 创建client

    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token

    client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()


    # 构造请求对象

    request: ListDocumentBlockRequest = ListDocumentBlockRequest.builder() \

        .document_id("KREmwsK9LiuqYnk4ek5cX1eKnFx") \
        .page_size(500) \
        .document_revision_id(-1) \
        .build()

    # 发起请求

    option = lark.RequestOption.builder().user_access_token("u-fOLq7HbFV4iaXOR15dkX8R140S9h5h2NOq20k5u20azm").build()

    response: ListDocumentBlockResponse = client.docx.v1.document_block.list(request, option)

    # 处理失败返回

    if not response.success():
        lark.logger.error(f"client.docx.v1.document_block.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")

        return


    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
  

if __name__ == "__main__":
    main()
```
可以返回这个文档的所有块结构：
```json
{

  "code": 0,

  "data": {

    "has_more": false,

    "items": [

      {

        "block_id": "RZmswykiNiALQhkKqeFc798unDf",

        "block_type": 1,

        "children": [

          "EYVidHRNXoT925xS5gSc1yhxnAg",

          "TbfidWHOGosfGkxQB8EcUkpRnFh",

          "LwvRdwzU3of4ggxXS9XcX8kFnPh",

          "VU4Wd06xcoTuHhxrKq1c8USEndQ",

          "C1SIdLNLloxtSKxweaNclTJCnZe",

          "ZEm9dN7rIo9xpMxh9Q5csLXAnVs",

          "EC4vdTYPPoC3aDxJrfacsWtVngg",

          "QQjcd7uEgoEgPOxwjSfc1ZkKnog",

          "Eic9deRhqoXJ7axWJ32cHRtRnzc",

          "JZBhdWE1dov8u5x4weZcu6gbnHb",

          "VXwrdGgZtoQQ0txKJuHciub2noc",

          "KOV8dkyrzoWVOUxKM2jcZ1EVnoe",

          "Y9BgdJE8loSuXuxCvnFc1DfGnTc",

          "GMjhdj2GuoIE0IxBdRxclN5AnEe",

          "UjPddFbzLoQr79xKCR3cldAunKc"

        ],

        "page": {

          "elements": [

            {

              "text_run": {

                "content": "RGB565转JPEG",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1

          }

        },

        "parent_id": ""

      },

      {

        "block_id": "EYVidHRNXoT925xS5gSc1yhxnAg",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "重要参考",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "TbfidWHOGosfGkxQB8EcUkpRnFh",

        "block_type": 999,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "undefined": {}

      },

      {

        "block_id": "LwvRdwzU3of4ggxXS9XcX8kFnPh",

        "block_type": 34,

        "children": [

          "AZRQdJCRQokoMaxOqHoc2IQdn5g",

          "NkUddwAEmoW3gIxbTZIcjeMhnCg"

        ],

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "quote_container": {}

      },

      {

        "block_id": "AZRQdJCRQokoMaxOqHoc2IQdn5g",

        "block_type": 4,

        "heading2": {

          "elements": [

            {

              "text_run": {

                "content": "ESP32 是否支持使用不带 JEPG 编码的摄像头来获取 JPEG 图像？",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        },

        "parent_id": "LwvRdwzU3of4ggxXS9XcX8kFnPh"

      },

      {

        "block_id": "NkUddwAEmoW3gIxbTZIcjeMhnCg",

        "block_type": 2,

        "parent_id": "LwvRdwzU3of4ggxXS9XcX8kFnPh",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "如果摄像头本身不支持 JPEG 编码，可以参考我们提供的 ",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "esp-iot-solution/examples/camera/pic_server",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "link": {

                    "url": "https%3A%2F%2Fgithub.com%2Fespressif%2Fesp-iot-solution%2Ftree%2Fmaster%2Fexamples%2Fcamera%2Fpic_server"

                  },

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": " 例程，在 ESP32 设备上实现软件 JPEG 编码。该方法通过软件对 YUV422 或 RGB565 数据进行编码，得到 JPEG 图像。",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "VU4Wd06xcoTuHhxrKq1c8USEndQ",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "现在在main程序中将fb输出改为RGB565格式输出：",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "C1SIdLNLloxtSKxweaNclTJCnZe",

        "block_type": 14,

        "code": {

          "elements": [

            {

              "text_run": {

                "content": ".pixel_format = PIXFORMAT_RGB565",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "language": 10,

            "wrap": false

          }

        },

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf"

      },

      {

        "block_id": "ZEm9dN7rIo9xpMxh9Q5csLXAnVs",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "要想在HTML中直接显示，直接调用",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "fmt2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "函数即可。",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "EC4vdTYPPoC3aDxJrfacsWtVngg",

        "block_type": 14,

        "code": {

          "elements": [

            {

              "text_run": {

                "content": "/* 转换RGB565为JPEG格式 */\n",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "bool convert_result = fmt2jpg(fb->buf, fb->len, fb->width, fb->height, fb->format, 80, &jpeg_buf, &jpeg_len);",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "language": 10,

            "wrap": false

          }

        },

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf"

      },

      {

        "block_id": "QQjcd7uEgoEgPOxwjSfc1ZkKnog",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "fmt2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "函数在",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "to_jpg.cpp",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "函数中实现。",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "Eic9deRhqoXJ7axWJ32cHRtRnzc",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "在",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "to_jpg.cpp",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "中还有一个",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "frame2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "函数，功能和",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "fmt2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "一致，区别在于",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "frame2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "是对",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "fmt2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "功能的封装，可以自动从fb中解析各种参数，无需像",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "fmt2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "中需要手动全部指定图片参数。",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "JZBhdWE1dov8u5x4weZcu6gbnHb",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "最重要的是需要在显示图片后手动释放内存，否则会造成内存泄露。",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "VXwrdGgZtoQQ0txKJuHciub2noc",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "当前模式的内存分配：",

                "text_element_style": {

                  "bold": true,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "KOV8dkyrzoWVOUxKM2jcZ1EVnoe",

        "block_type": 14,

        "code": {

          "elements": [

            {

              "text_run": {

                "content": "1. 摄像头硬件 → RGB565缓冲区 (fb->buf)\n   ↓\n2. fmt2jpg()函数 → 动态分配JPEG缓冲区 (jpeg_buf)\n   ↓\n",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "3. 发送完成后 → 需要释放两个缓冲区",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "language": 30,

            "wrap": false

          }

        },

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf"

      },

      {

        "block_id": "Y9BgdJE8loSuXuxCvnFc1DfGnTc",

        "block_type": 2,

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "直接JPEG模式的内存分配：",

                "text_element_style": {

                  "bold": true,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      },

      {

        "block_id": "GMjhdj2GuoIE0IxBdRxclN5AnEe",

        "block_type": 14,

        "code": {

          "elements": [

            {

              "text_run": {

                "content": "1. 摄像头硬件 → 直接生成JPEG缓冲区 (fb->buf)\n   ↓\n",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "2. 发送完成后 → 只需释放一个缓冲区",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "language": 30,

            "wrap": false

          }

        },

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf"

      },

      {

        "block_id": "UjPddFbzLoQr79xKCR3cldAunKc",

        "block_type": 19,

        "callout": {

          "background_color": 12,

          "emoji_id": "face_in_clouds"

        },

        "children": [

          "DsBIda24Lo75kJxAhTZcSPmunIf"

        ],

        "parent_id": "RZmswykiNiALQhkKqeFc798unDf"

      },

      {

        "block_id": "DsBIda24Lo75kJxAhTZcSPmunIf",

        "block_type": 2,

        "parent_id": "UjPddFbzLoQr79xKCR3cldAunKc",

        "text": {

          "elements": [

            {

              "text_run": {

                "content": "fmt2jpg",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "使用",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "malloc",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "动态分配内存，所以需要手动",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "free",

                "text_element_style": {

                  "bold": false,

                  "inline_code": true,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            },

            {

              "text_run": {

                "content": "释放！",

                "text_element_style": {

                  "bold": false,

                  "inline_code": false,

                  "italic": false,

                  "strikethrough": false,

                  "underline": false

                }

              }

            }

          ],

          "style": {

            "align": 1,

            "folded": false

          }

        }

      }

    ]

  },

  "msg": "success"

}
```
现在我就可以接些这个json结构，提取出其中的markdown结构，然后输出一个markdown文件。

# 期望的结果
我希望最终的成品是一个可视化的应用，使用tkinter也行，第一步还不需要太好看，允许用户输入自己的user_accsee_token，和文档的document_id，然后解析后输出排版好的markdown文件。

你来帮我实现，飞书文档提供很多API结构，包括有哪些块类型，你又不会的就问我。或者参考下面的文档
https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/list